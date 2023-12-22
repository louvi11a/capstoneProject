var orphans = window.ORPHANS;
var sentiment_scores = window.SENTIMENT_SCORES;

var ctxPie = document.getElementById('pieChart').getContext('2d');
// ... rest of your code
var pieChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
        labels: orphans,
        datasets: [{
            data: sentiment_scores,
            // ... rest of your pie chart configuration
        }]
    },
    // ... rest of your pie chart options
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Sentiment Scores'
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return orphans[tooltipItem.dataIndex] + ': ' + sentiment_scores[tooltipItem.dataIndex].toFixed(3);
                    }
                }
            }
        }
    }
});

var ctxBar = document.getElementById('barChart').getContext('2d');
var barChart = new Chart(ctxBar, {
    type: 'bar',
    data: {
        labels: orphans,
        datasets: [{
            data: sentiment_scores,
            // ... rest of your bar chart configuration
        }]
    },
    // ... rest of your bar chart options
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Sentiment Scores per Orphan'
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return 'Sentiment Score: ' + tooltipItem.parsed.ytoFixed(3);
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

document.getElementById('switchChartPie').addEventListener('click', function() {
    document.getElementById('pieChartContainer').style.display = 'none';
    document.getElementById('barChartContainer').style.display = 'block';
});

document.getElementById('switchChartBar').addEventListener('click', function() {
    document.getElementById('barChartContainer').style.display = 'none';
    document.getElementById('pieChartContainer').style.display = 'block';
});