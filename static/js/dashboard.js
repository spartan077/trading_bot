let capitalChart, profitChart, tradeCountChart;
let simulationRunning = false;
let chartsInitialized = false;

// Base URL for API calls
const API_BASE_URL = window.location.origin;

function initializeCharts() {
    if (chartsInitialized) return;

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true,
        height: 300,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 8
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    };

    // Initialize Capital Chart
    capitalChart = new Chart(
        document.getElementById('capitalChart').getContext('2d'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Capital',
                    data: [],
                    borderColor: '#007bff',
                    tension: 0.1
                }]
            },
            options: chartOptions
        }
    );

    // Initialize Profit Chart
    profitChart = new Chart(
        document.getElementById('profitChart').getContext('2d'),
        {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Daily Profit/Loss',
                    data: [],
                    backgroundColor: '#28a745',
                }]
            },
            options: chartOptions
        }
    );

    // Initialize Trade Count Chart
    tradeCountChart = new Chart(
        document.getElementById('tradeCountChart').getContext('2d'),
        {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Number of Trades',
                    data: [],
                    backgroundColor: '#17a2b8',
                }]
            },
            options: chartOptions
        }
    );

    chartsInitialized = true;
}

async function startSimulation() {
    console.log("Starting simulation...");
    const button = document.getElementById('startSimulation');
    button.disabled = true;
    button.textContent = 'Simulating...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/start_simulation`);
        const result = await response.json();
        console.log("Simulation response:", result);

        if (result.status === 'success') {
            await updateMetrics();
            await updateTradesTable();
            await updateCharts();
            console.log("Simulation completed successfully");
        } else {
            console.error("Simulation failed:", result.error);
            alert('Simulation failed: ' + result.error);
        }
    } catch (error) {
        console.error("Error during simulation:", error);
        alert('Error during simulation: ' + error.message);
    } finally {
        button.disabled = false;
        button.textContent = 'Start Simulation';
    }
}

async function resetSimulation() {
    console.log("Resetting simulation...");
    const resetButton = document.getElementById('resetSimulation');
    resetButton.disabled = true;
    resetButton.textContent = 'Resetting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/reset_simulation`);
        const result = await response.json();
        
        if (result.status === 'success') {
            // Reset all charts
            if (chartsInitialized) {
                capitalChart.data.labels = [];
                capitalChart.data.datasets[0].data = [];
                capitalChart.update();
                
                profitChart.data.labels = [];
                profitChart.data.datasets[0].data = [];
                profitChart.update();
                
                tradeCountChart.data.labels = [];
                tradeCountChart.data.datasets[0].data = [];
                tradeCountChart.update();
            }
            
            // Reset metrics and table
            await updateMetrics();
            await updateTradesTable();
            
            console.log("Reset completed successfully");
        } else {
            console.error("Reset failed:", result.message);
            alert('Reset failed: ' + result.message);
        }
    } catch (error) {
        console.error("Error during reset:", error);
        alert('Error during reset: ' + error.message);
    } finally {
        resetButton.disabled = false;
        resetButton.textContent = 'Reset Simulation';
    }
}

async function setInitialCapital() {
    console.log("Setting initial capital...");
    const capital = document.getElementById('initialCapital').value;
    try {
        const response = await fetch(`${API_BASE_URL}/api/set_capital`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ capital: parseInt(capital) })
        });
        
        if (response.ok) {
            document.getElementById('capitalModal').style.display = 'none';
            document.getElementById('startSimulation').disabled = false;
            initializeCharts();
            await updateMetrics();
            console.log("Initial capital set successfully");
        }
    } catch (error) {
        console.error("Error setting initial capital:", error);
        alert('Error setting initial capital: ' + error.message);
    }
}

async function updateMetrics() {
    const response = await fetch(`${API_BASE_URL}/api/metrics`);
    const metrics = await response.json();
    
    document.getElementById('totalTrades').textContent = metrics.total_trades;
    document.getElementById('successRate').textContent = `${metrics.success_rate.toFixed(2)}%`;
    document.getElementById('profitLoss').textContent = `₹${metrics.profit_loss.toFixed(2)}`;
    document.getElementById('finalCapital').textContent = `₹${metrics.final_capital.toFixed(2)}`;
}

async function updateTradesTable() {
    const response = await fetch(`${API_BASE_URL}/api/trades`);
    const trades = await response.json();
    
    const tbody = document.querySelector('#tradesTable tbody');
    tbody.innerHTML = '';
    
    trades.slice(-10).forEach(trade => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(trade.date).toLocaleDateString()}</td>
            <td>${trade.stock}</td>
            <td>${trade.type}</td>
            <td>₹${trade.price.toFixed(2)}</td>
            <td>${trade.quantity}</td>
            <td>₹${trade.value.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

async function updateCharts() {
    if (!chartsInitialized) return;

    const response = await fetch(`${API_BASE_URL}/api/chart_data`);
    const chartData = await response.json();
    
    // Limit the number of data points to display
    const maxDataPoints = 20;
    const startIdx = Math.max(0, chartData.dates.length - maxDataPoints);
    
    const dates = chartData.dates.slice(startIdx);
    const capital = chartData.capital.slice(startIdx);
    const profits = chartData.profits.slice(startIdx);
    const tradeCounts = chartData.trade_counts.slice(startIdx);

    // Update Capital Chart
    capitalChart.data.labels = dates;
    capitalChart.data.datasets[0].data = capital;
    capitalChart.update();
    
    // Update Profit Chart
    profitChart.data.labels = dates;
    profitChart.data.datasets[0].data = profits;
    profitChart.update();
    
    // Update Trade Count Chart
    tradeCountChart.data.labels = dates;
    tradeCountChart.data.datasets[0].data = tradeCounts;
    tradeCountChart.update();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded, initializing...");
    
    // Add event listeners for buttons
    const startButton = document.getElementById('startSimulation');
    const resetButton = document.getElementById('resetSimulation');
    
    startButton.addEventListener('click', startSimulation);
    resetButton.addEventListener('click', resetSimulation);
    
    updateMetrics();
    updateTradesTable();
});

// Update every minute if charts are initialized
setInterval(() => {
    if (chartsInitialized) {
        updateMetrics();
        updateTradesTable();
        updateCharts();
    }
}, 60000); 