document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const history = document.getElementById('historyInput').value.trim();
    const btn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');

    if (!history) return alert('Please enter a watch history sequence.');

    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    resultsSection.classList.remove('active');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history })
        });

        const data = await response.json();
        
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            renderResults(data);
            resultsSection.classList.add('active');
        }
    } catch (error) {
        alert("Failed to connect to backend.");
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze & Recommend';
    }
});

function renderResults(data) {
    const grid = document.getElementById('resultsGrid');
    grid.innerHTML = '';

    const fields = [
        { label: 'Current Reel', value: data.current_reel, fullWidth: true },
        { label: 'Interest Detected', value: data.interest_detected, fullWidth: true },
        { label: 'Why', value: data.why, fullWidth: true },
        { label: 'Recommended Tech Reel', value: data.recommended_tech_reel, fullWidth: true },
        { label: 'Category', value: data.category },
        { label: 'Difficulty', value: data.difficulty },
        { label: 'Confidence', value: data.confidence, isConfidence: true },
        { label: 'Why This Recommendation', value: data.why_this_recommendation, fullWidth: true }
    ];

    fields.forEach(field => {
        const item = document.createElement('div');
        item.className = `result-item ${field.fullWidth ? 'full-width' : ''}`;
        
        if (field.isConfidence) {
            const conf = field.value.toLowerCase();
            if (conf.includes('high')) item.classList.add('confidence-high');
            else if (conf.includes('medium')) item.classList.add('confidence-medium');
            else item.classList.add('confidence-low');
        }

        item.innerHTML = `<div class="result-label">${field.label}</div><div class="result-value">${field.value}</div>`;
        grid.appendChild(item);
    });
}