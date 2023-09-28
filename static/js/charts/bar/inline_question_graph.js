function inlineQuestionGraph(inlineQuestionData, inlineQuestionCanvasId) {

    console.log(inlineQuestionData)
    
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

    scrollableVerticalBarChart(inlineQuestionCanvasId, data, originChartConfig);
}