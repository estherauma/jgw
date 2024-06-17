function inlineQuestionGraph(inlineQuestionData, inlineQuestionCanvasId) {
    
    const data = inlineQuestionData.counts
    const labels = inlineQuestionData.labels
    

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'RESPONSES',
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
                    right: 30,
                    bottom: 20,
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

    scrollableVerticalBarChart(inlineQuestionCanvasId, data, originChartConfig);
}