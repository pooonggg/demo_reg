document.addEventListener('DOMContentLoaded', () => {
    let ingredientList = [];
    const elements = {
        addButton: document.getElementById('add-ingredient-btn'),
        form: document.getElementById('ingredient-form'),
        ingredientTable: document.getElementById('ingredient-table'),
        resultsContainer: document.getElementById('results-container'),
        resultsTable: document.getElementById('results-table')
    };

    // Initialize system
    const initSystem = async () => {
        try {
            const response = await fetch('/get-ingredient-list');
            ingredientList = await response.json();
            initAutocomplete();
            setupEventListeners();
        } catch (error) {
            console.error('Error loading ingredients:', error);
        }
    };

    // Autocomplete setup
    const initAutocomplete = () => {
        const datalist = document.getElementById('ingredient-list');
        datalist.innerHTML = ingredientList.map(ingredient => 
            `<option value="${ingredient}">${ingredient}</option>`
        ).join('');
    };

    // Add new ingredient row
    const addNewRow = () => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" class="inci-input" placeholder="Search INCI name" list="ingredient-list"></td>
            <td><input type="number" class="concentration-input" placeholder="0.0" step="0.1"></td>
        `;
        newRow.style.opacity = '0';
        newRow.style.transform = 'translateY(-10px)';
        elements.ingredientTable.querySelector('tbody').appendChild(newRow);
        
        setTimeout(() => {
            newRow.style.opacity = '1';
            newRow.style.transform = 'translateY(0)';
        }, 50);
    };

    // Form validation
    const validateForm = () => {
        let isValid = true;
        document.querySelectorAll('.inci-input, .concentration-input').forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = 'var(--error-red)';
                isValid = false;
            } else {
                input.style.borderColor = '';
            }
        });
        return isValid;
    };

    // Submit form
    const submitForm = async () => {
        const ingredients = Array.from(
            elements.ingredientTable.querySelectorAll('tbody tr')
        ).map(row => ({
            INCI: row.querySelector('.inci-input').value,
            concentration: parseFloat(row.querySelector('.concentration-input').value)
        }));

        try {
            const response = await fetch('/check-regulations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ingredients })
            });
            
            const results = await response.json();
            renderResults(results);
        } catch (error) {
            alert('Error submitting form: ' + error.message);
        }
    };

    // Render results
    const renderResults = (results) => {
        const tbody = elements.resultsTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        results.forEach((result, index) => {
            const row = document.createElement('tr');
            row.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s forwards`;
            // ในส่วน renderResults
            row.innerHTML = `
                <td>${result.index}</td> <!-- แสดงลำดับจาก JSON -->
                <td>${result.INCI}</td>
                <td>${result.CAS_Number}</td>
                <td>
                    ${result.regulation_pass === 'Pass' ? 
                        '<svg class="status-icon check-icon"><use xlink:href="#check-icon"></use></svg>' : 
                        '<svg class="status-icon cross-icon"><use xlink:href="#cross-icon"></use></svg>'}
                </td>
                <td>
                    ${result.laws.map(law => `
                        <div class="law-item ${law.color}-bg">
                            ${law.text}
                        </div>
                    `).join('')}
                </td>
                `;

            tbody.appendChild(row);
        });
        
        elements.resultsContainer.style.display = 'block';
        window.scrollTo({
            top: elements.resultsContainer.offsetTop - 100,
            behavior: 'smooth'
        });
    };

    // Event listeners
    const setupEventListeners = () => {
        elements.addButton.addEventListener('click', addNewRow);
        
        elements.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (validateForm()) {
                await submitForm();
            }
        });
        
        document.addEventListener('input', (e) => {
            if (e.target.matches('.inci-input, .concentration-input')) {
                e.target.style.borderColor = e.target.value.trim() ? '' : 'var(--error-red)';
            }
        });
    };

    // Initialize
    initSystem();
});