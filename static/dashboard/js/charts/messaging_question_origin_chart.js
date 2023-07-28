
function messagingQuestionOriginChart(originChartData) {
    const data = originChartData["data"]
    const labels = originChartData["labels"]
    
    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'RESPONSES',
                data: data,
                backgroundColor: COLORS.skyBlue,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        drawTicks: true,
                        display: false
                    },
                    autoSkip: false,
                    maxTicksLimit: 5
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: COLORS.navyBlue,
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            maintainAspectRatio: false,
            responsive: true,
        },
        plugins: {
            legend: {
                display: false
            },
            scrollbar: {
                enabled: true
            }
        }
    }
    scrollableVerticalBarChart('messaging_question_origin_graphcard', data, originChartConfig)
}