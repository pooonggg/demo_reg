from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def load_ingredients(filename):
    with open(f'reg_json/{filename}', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'ประกาศกระทรวงสาธารณสุข_วัตถุที่อาจใช้เป็นส่วนผสม' in data:
            return data['ประกาศกระทรวงสาธารณสุข_วัตถุที่อาจใช้เป็นส่วนผสม']
        return data['ประกาศกระทรวงสาธารณสุข_วัตถุที่ห้ามใช้เป็นส่วนผสม']

allowed_ingredients = load_ingredients('May_use.json')
forbidden_ingredients = load_ingredients('Not_use.json')

@app.route('/check_regulation')
def index():
    return render_template('index.html')

@app.route('/check_regulation/get-ingredient-list')
def get_ingredient_list():
    allowed_names = [name for item in allowed_ingredients for name in item['ชื่อวัตถุ']['ชื่อทั่วไป']]
    forbidden_names = [name for item in forbidden_ingredients for name in item['ชื่อวัตถุ']['ชื่อทั่วไป']]
    return jsonify(list(set(allowed_names + forbidden_names)))

def check_regulations(ingredients):
    results = []
    for ing in ingredients:
        inci = ing['INCI']
        conc = float(ing.get('concentration', 0))
        
        # Check forbidden list
        forbidden = next((item for item in forbidden_ingredients if inci in item['ชื่อวัตถุ']['ชื่อทั่วไป']), None)
        if forbidden:
            results.append({
                "index": forbidden['ลำดับ'],  # ใช้ลำดับจาก JSON
                "INCI": inci,
                "CAS_Number": forbidden['ชื่อวัตถุ'].get('CAS Number', '-'),
                "regulation_pass": "Forbidden",
                "laws": [
                    {
                        "text": "กฏหมาย: บัญชีแนบท้ายประกาศกระทรวงสาธารณสุข เรื่อง กำหนดชื่อ ปริมาณ และเงื่อนไขของวัตถุที่ห้ามใช้เป็นส่วนผสมในการผลิตเครื่องสำอาง",
                        "color": "red"
                    }
                ]
            })
            continue
            
        # Check allowed list
        allowed = next((item for item in allowed_ingredients if inci in item['ชื่อวัตถุ']['ชื่อทั่วไป']), None)
        if allowed:
            passed_usages = []
            exceeded_usages = []
            
            for usage in allowed['รายละเอียดการใช้งาน']:
                usage_max = float(usage['ความเข้มข้นสูงสุด'].replace('%', ''))
                if conc > usage_max:
                    exceeded_usages.append(usage)
                else:
                    passed_usages.append(usage)

            # สร้างข้อมูลกฎหมาย
            laws = [{
                "text": "กฏหมาย: บัญชีแนบท้ายประกาศกระทรวงสาธารณสุข เรื่อง กำหนดชื่อ ปริมาณ และเงื่อนไขของวัตถุที่อาจใช้เป็นส่วนผสมในการผลิตเครื่องสําอาง",
                "color": "green" if not exceeded_usages else "yellow"
            }]
            
            if exceeded_usages:
                laws.extend({
                    "text": f"{usage['บริเวณที่ใช้']} (สูงสุด {usage['ความเข้มข้นสูงสุด']})",
                    "color": "yellow"
                } for usage in exceeded_usages)
                regulation_status = "Forbidden"
            else:
                laws.extend({
                    "text": f"{usage['บริเวณที่ใช้']} (สูงสุด {usage['ความเข้มข้นสูงสุด']})",
                    "color": "green"
                } for usage in passed_usages)
                regulation_status = "Pass"
            
            results.append({
                "index": allowed['ลำดับ'],  # ใช้ลำดับจาก JSON
                "INCI": inci,
                "CAS_Number": allowed['ชื่อวัตถุ']['CAS Number'].get(inci, '-'),
                "regulation_pass": regulation_status,
                "laws": laws
            })
        else:
            results.append({
                "index": "-",
                "INCI": inci,
                "CAS_Number": "-",
                "regulation_pass": "Pass",
                "laws": []
            })
    
    return results

@app.route('/check_regulation/check-regulations', methods=['POST'])
def check_regulations_route():
    ingredients = request.json.get('ingredients', [])
    results = check_regulations(ingredients)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
