function inlineQuestionLanguageGraph(langaugeData) {
    const data = langaugeData["counts"]
    const labels = langaugeData["labels"]
    

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

    scrollableVerticalBarChart('inline-question-language-graph-id', data, chartConfig)
    
}