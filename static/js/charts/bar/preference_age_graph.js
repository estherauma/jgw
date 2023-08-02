function preferenceAgeGraph(preferenceAgeGraphData) {
    console.log(preferenceAgeGraphData)
    const data = preferenceAgeGraphData["counts"];
    const chartConfig =  {
        type: 'bar',
        data: {
            labels: preferenceAgeGraphData["labels"],
            datasets: [{
                label: 'NUMBER OF USERS',
                data: data,
                backgroundColor: '#37C1E3',
                barThickness: 15,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: 'red',
                        fontSize: 12
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        borderDash: [2],
                        drawBorder: false,
                        borderWidth: 0,
                        borderDash: [],
                        borderDashOffset: 0,
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
                        fontColor: '#193560',
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }

    scrollableVerticalBarChart('preference-age-graph-id', data, chartConfig)
}