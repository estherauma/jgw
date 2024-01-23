function inlineQuestionOriginGraph(chartData) {
    const data = chartData["counts"]
    const labels = chartData["labels"]
    

    const chartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
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

    scrollableVerticalBarChart('inline-question-destination-graph-id', data, chartConfig)

}