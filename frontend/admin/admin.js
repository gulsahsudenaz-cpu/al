// Admin Panel JavaScript
const API_BASE_URL = 'http://localhost:8000/v1';

// Sidebar Toggle
document.getElementById('toggleSidebar').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('show');
});

// Load Dashboard Data
async function loadDashboard() {
    try {
        // Load metrics
        const metricsResponse = await fetch(`${API_BASE_URL}/admin/metrics/rag`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (metricsResponse.ok) {
            const metrics = await metricsResponse.json();
            updateDashboard(metrics);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateDashboard(metrics) {
    // Update RAG hit rate
    const hitRate = metrics.avg_hit_rate * 100;
    document.getElementById('ragHitRate').textContent = `${hitRate.toFixed(1)}%`;
    
    // Update chart
    updateChart(metrics);
}

// Chart
const ctx = document.getElementById('aiChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'],
        datasets: [{
            label: 'AI Doğruluk %',
            data: [92, 94, 91, 96, 95, 97, 98],
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                max: 100
            }
        }
    }
});

function updateChart(metrics) {
    // Update chart with real data
    // chart.data.datasets[0].data = metrics.data;
    // chart.update();
}

// Simulate live chat updates
setInterval(() => {
    const chat = document.getElementById('liveChat');
    if (Math.random() > 0.7 && chat) {
        const msg = document.createElement('div');
        msg.className = 'msg-user';
        msg.textContent = ['Evet', 'Teşekkürler', 'Tamam'][Math.floor(Math.random() * 3)];
        chat.appendChild(msg);
        chat.scrollTop = chat.scrollHeight;
    }
}, 8000);

// Initialize
window.addEventListener('load', () => {
    loadDashboard();
});

