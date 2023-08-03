function preferenceOriginGraph(preferenceDestinationData) {
    const data = preferenceDestinationData["counts"]
    const labels = preferenceDestinationData["labels"]
    

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

    scrollableVerticalBarChart('preference-origin-graph-id', data, originChartConfig);
}