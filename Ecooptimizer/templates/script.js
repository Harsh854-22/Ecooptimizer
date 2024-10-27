function fetchData(endpoint) {
    return fetch(`/api/${endpoint}`).then(response => response.json());
}

function updateCharts() {
    // Update usage chart
    fetchData('usage_data').then(data => {
        const traces = [];
        const serverIds = [...new Set(data.map(d => d.server_id))];
        
        serverIds.forEach(serverId => {
            const serverData = data.filter(d => d.server_id === serverId);
            traces.push({
                x: serverData.map(d => new Date(d.timestamp)),
                y: serverData.map(d => d.usage),
                type: 'scatter',
                mode: 'lines+markers',
                name: `Server ${serverId}`
            });
        });

        Plotly.newPlot('usage-chart', traces, {
            title: 'Real-time Server Usage',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Usage' }
        });
    });

    // Update optimization chart
    fetchData('optimize').then(data => {
        const trace1  = {
            x: data.map(d => `Server ${d.server_id}`),
            y: data.map(d => d.allocated_load),
            name: 'Allocated Load',
            type: 'bar'
        };

        const trace2 = {
            x: data.map(d => `Server ${d.server_id}`),
            y: data.map(d => d.energy_consumption),
            name: 'Energy Consumption',
            type: 'bar'
        };

        Plotly.newPlot('optimization-chart', [trace1, trace2], {
            title: 'Load Optimization Results',
            xaxis: { title: 'Server' },
            yaxis: { title: 'Load / Energy' },
            barmode: 'group'
        });
    });

    // Update prediction chart
    fetchData('predict_load').then(data => {
        const currentTime = new Date();
        const trace = {
            x: [currentTime, new Date(currentTime.getTime() + 60*60*1000)],
            y: [null, data.predicted_load],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Predicted Load'
        };

        Plotly.newPlot('prediction-chart', [trace], {
            title: 'Load Prediction (Next Hour)',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Predicted Load' }
        });
    });
}

function updateMetrics() {
    fetchData('usage_data').then(usageData => {
        fetchData('optimize').then(optimizationData => {
            const totalUsage = usageData.reduce((sum, d) => sum + d.usage, 0);
            const totalCapacity = 450; // Sum of all server capacities
            const utilizationRate = (totalUsage / totalCapacity) * 100;

            const totalEnergyConsumption = usageData.reduce((sum, d) => sum + d.energy_consumption, 0);
            const optimizedEnergyConsumption = optimizationData.reduce((sum, d) => sum + d.energy_consumption, 0);
            const energySavings = ((totalEnergyConsumption - optimizedEnergyConsumption) / totalEnergyConsumption) * 100;

            const metricsContainer = document.getElementById('metrics-container');
            metricsContainer.innerHTML = `
                <div class="metric-card">
                    <h3>Server Utilization Rate</h3>
                    <p class="metric-value">${utilizationRate.toFixed(2)}%</p>
                </div>
                <div class="metric-card">
                    <h3>Energy Savings</h3>
                    <p class="metric-value">${energySavings.toFixed(2)}%</p>
                </div>
                <div class="metric-card">
                    <h3>Total Energy Consumption</h3>
                    <p class="metric-value">${totalEnergyConsumption.toFixed(2)} kWh</p>
                </div>
            `;
        });
    });
}

function initDashboard() {
    updateCharts();
    updateMetrics();
    setInterval(() => {
        updateCharts();
        updateMetrics();
    }, 5000); // Update every 5 seconds
}

window.addEventListener('load', initDashboard);