// bar-chart.js

// Sample data for the bar chart
const barChartData = {
    labels: ['Label 1', 'Label 2', 'Label 3', 'Label 4', 'Label 5'],
    datasets: [{
        label: 'Bar Chart',
        data: [20, 40, 15, 30, 25], // Initial data
        backgroundColor: 'rgba(52, 152, 219, 0.7)', // Bar color
    }],
};

// Configuration for the bar chart
const barChartConfig = {
    type: 'bar',
    data: barChartData,
    options: {
        scales: {
            y: {
                beginAtZero: true,
            },
        },
    },
};

// Create the bar chart
const barChartCanvas = document.getElementById('barChart-1');
const barChart = new Chart(barChartCanvas.getContext('2d'), barChartConfig);

// Simulate dynamic data for the bar chart
setInterval(() => {
    const newData = barChartData.datasets[0].data.map(() => Math.floor(Math.random() * 100));
    barChart.data.datasets[0].data = newData;
    barChart.update();
}, 3000); // Update the data every 3 seconds
