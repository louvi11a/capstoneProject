// pie-chart.js

// Sample data for the pie chart
const pieChartData = {
    labels: ['Label 1', 'Label 2', 'Label 3', 'Label 4', 'Label 5'],
    datasets: [{
        data: [20, 40, 15, 30, 25], // Initial data
        backgroundColor: [
            'rgba(52, 152, 219, 0.7)',
            'rgba(46, 204, 113, 0.7)',
            'rgba(155, 89, 182, 0.7)',
            'rgba(230, 126, 34, 0.7)',
            'rgba(241, 196, 15, 0.7)',
        ], // Pie slice colors
    }],
};

// Configuration for the pie chart
const pieChartConfig = {
    type: 'pie',
    data: pieChartData,
};

// Create the pie chart
const pieChartCanvas = document.getElementById('pieChart-1');
pieChartCanvas.width = 200; // Set the canvas width
pieChartCanvas.height = 200; // Set the canvas height
const pieChart = new Chart(pieChartCanvas.getContext('2d'), pieChartConfig);

// Simulate dynamic data for the pie chart
setInterval(() => {
    const newData = pieChartData.datasets[0].data.map(() => Math.floor(Math.random() * 100));
    pieChart.data.datasets[0].data = newData;
    pieChart.update();
}, 3000); // Update the data every 3 seconds
