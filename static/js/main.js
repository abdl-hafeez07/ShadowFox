document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize Particles.js if element exists
    if(document.getElementById('particles-js')) {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 50, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": ["#4e54c8", "#8f94fb", "#00f2fe"] },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.4, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#ffffff", "opacity": 0.05, "width": 1 },
                "move": { "enable": true, "speed": 1, "direction": "none", "random": true, "out_mode": "out" }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": { "enable": true, "mode": "grab" },
                    "onclick": { "enable": true, "mode": "push" }
                },
                "modes": {
                    "grab": { "distance": 140, "line_linked": { "opacity": 0.3 } }
                }
            },
            "retina_detect": true
        });
    }

    // 2. Update Discount Value Display
    const discountRange = document.getElementById('discount');
    const discountVal = document.getElementById('discountVal');
    
    if(discountRange && discountVal) {
        discountRange.addEventListener('input', function() {
            // Display percentage
            discountVal.textContent = (parseFloat(this.value) * 100).toFixed(0) + '%';
        });
        // Init value
        discountVal.textContent = (parseFloat(discountRange.value) * 100).toFixed(0) + '%';
    }

    // 3. Dynamic Sub-Category population
    const categorySelect = document.getElementById('category');
    const subCategorySelect = document.getElementById('sub_category');

    if(categorySelect && subCategorySelect) {
        const subCategories = {
            'Furniture': ['Bookcases', 'Chairs', 'Furnishings', 'Tables'],
            'Office Supplies': ['Appliances', 'Art', 'Binders', 'Envelopes', 'Fasteners', 'Labels', 'Paper', 'Storage', 'Supplies'],
            'Technology': ['Accessories', 'Copiers', 'Machines', 'Phones']
        };

        categorySelect.addEventListener('change', function() {
            const selectedCat = this.value;
            subCategorySelect.innerHTML = '<option value="" selected disabled>Select Sub-Category</option>';
            
            if(subCategories[selectedCat]) {
                subCategories[selectedCat].forEach(sub => {
                    const option = document.createElement('option');
                    option.value = sub;
                    option.textContent = sub;
                    subCategorySelect.appendChild(option);
                });
            }
        });
    }

    // 4. Handle Prediction Form Submission Loading Animation
    const predictForm = document.getElementById('predictionForm');
    if(predictForm) {
        predictForm.addEventListener('submit', function(e) {
            // Check form validity before showing loading
            if(this.checkValidity()) {
                const overlay = document.getElementById('loadingOverlay');
                const text = document.getElementById('loadingText');
                
                if(overlay) {
                    overlay.classList.remove('d-none');
                    
                    // Simulate different loading stages for visual feedback
                    setTimeout(() => { text.textContent = "Extracting Features..."; }, 800);
                    setTimeout(() => { text.textContent = "Applying XGBoost Decision Trees..."; }, 1600);
                    setTimeout(() => { text.textContent = "Calculating Profitability Score..."; }, 2400);
                    
                    // The form will continue to submit to the server in the background.
                }
            }
        });
    }
});
