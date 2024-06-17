function emailClicksByUser(emailClicksByRoute) {
    const data = emailClicksByRoute["counts"]
    const labels = emailClicksByRoute["labels"]
    

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'CLICKS',
                data: data,
                backgroundColor: COLORS.navyBlue,
                barThickness: 15,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            layout: {
                padding: {
                    right: 50,
                }
            },
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                scrollbar: {
                    enabled: true
                }
            }
        }
    }

    scrollableVerticalBarChart('email-clicks-by-user-graph-id', data, originChartConfig);
}