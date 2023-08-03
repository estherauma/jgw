function preferenceLanguageGraph(langaugeData) {
    const data = langaugeData["counts"]
    const labels = langaugeData["labels"]
    

    const languageChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'PREFERENCES',
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

    scrollableVerticalBarChart('preference-language-graph-id', data, languageChartConfig)

}