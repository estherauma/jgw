function messagingQuestionOriginChart(originChartData) {
    const data = originChartData["counts"]
    const labels = originChartData["labels"]

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'RESPONSES',
                data: data,
                backgroundColor: COLORS.skyBlue,
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
                ...externalPluginsConfigDataTables(),
                legend: {
                    display: false
                },
                scrollbar: {
                    enabled: true
                }
            }
        },
        plugins: [ChartDataLabels],
    }
    scrollableVerticalBarChart('messaging-question-origin-chart-id', data, originChartConfig)
}