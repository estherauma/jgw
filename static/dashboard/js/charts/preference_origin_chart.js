function preferenceOriginChart(preferenceDestinationData) {
    const labels = preferenceDestinationData["labels"]
    const data = preferenceDestinationData["data"]

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'PREFERENCES',
                data: data,
                backgroundColor: COLORS.navyBlue,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                    },
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

    scrollableVerticalBarChart('preference_origin', data, originChartConfig);
}