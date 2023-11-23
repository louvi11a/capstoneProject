<script>
    var orphans = {{ orphans|safe }};
    var sentiment_scores = {{ sentiment_scores|safe }};

    var ctxPie = document.getElementById('pieChart').getContext('2d');
    var pieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: orphans,
            datasets: [{
                data: sentiment_scores,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',  // color for 'Positive'
                    'rgba(255, 206, 86, 0.2)',  // color for 'Neutral'
                    'rgba(255, 99, 132, 0.2)'   // color for 'Negative'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
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
                            return orphans[tooltipItem.dataIndex] + ': ' + sentiment_scores[tooltipItem.dataIndex];
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
                label: 'Sentiment Score',
                data: sentiment_scores,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
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
                            return 'Sentiment Score: ' + tooltipItem.parsed.y;
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
</script>