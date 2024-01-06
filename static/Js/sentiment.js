fetch('/path/to/sentiment_chart/view')
    .then(response => response.json())
    .then(data => {
        var ctxPie = document.getElementById('pieChart2').getContext('2d');
        var pieChart = new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: ['lightblue', 'lightcoral']  // Add more colors if needed
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Pie Chart'
                    }
                }
            }
        });
    });