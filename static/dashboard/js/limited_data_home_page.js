function uniqueAndReturningUsersGraph({ returning_data, unique_data, labels }) {
    var ctx = document.getElementById('unique-and-returning-users').getContext('2d');
    const languageChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                label: 'Number of Users',
                data: returning_data,
                backgroundColor: COLORS.navyBlue,
                borderWidth: 0,
                borderRadius: 20,
                borderSkipped: false,
                barThickness: 18,
                barPercentage: 0.8
            },{
                data: unique_data,
                borderWidth: 0,
                borderRadius: 20,
                borderSkipped: false,
                barThickness: 18,
                barPercentage: 0.8
            }
        ]
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: 'red',
                        fontSize: 12
                    },
                    grid: {
                        color: COLORS.lightGray,
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
                        fontColor: COLORS.navyBlue,
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }

    new Chart(ctx,languageChartConfig);
}

function plotLimitedHomePageDataCharts(chartData) {
    let chartDataKeys = Object.keys(chartData)
    chartDataKeys.map(chartDataKeys => {
        if (chartDataKeys === "age") {
            usageByAgeChart(chartData['age'])
        }

        if (chartDataKeys === "gender") {
            usageByGenderChart(chartData['gender'])
        }

        if (chartDataKeys === "language") {
            usageByLanguageChart(chartData['language'])
        }
    })
    
}

function usageByAgeChart(usageByAgeData) {
    var ctx = document.getElementById('usage-by-age-chart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: usageByAgeData["labels"],
            datasets: [{
                label: 'Number of Users',
                data: usageByAgeData["data"],
                backgroundColor: [COLORS.appleGreen, COLORS.mediumBlue, COLORS.lightGreen, COLORS.skyBlue, COLORS.navyBlue],
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function usageByGenderChart(genderGraphData) {
    const labels = genderGraphData["labels"]
    const data = genderGraphData["data"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'My First Dataset',
            data: data,
            backgroundColor: [COLORS.appleGreen,COLORS.skyBlue,COLORS.navyBlue]
        }]
    };
    const config = {
        type: 'doughnut',
        data: chartData,
        options: {
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    var ctx = document.getElementById('usage-by-gender-chart').getContext('2d');
    new Chart(ctx, config)
}

function usageByLanguageChart(langaugeData) {
    const data = langaugeData["data"]
    const labels = langaugeData["labels"]
    

    var ctx = document.getElementById('usage-by-language-chart').getContext('2d');
    const languageChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users',
                data: data,
                backgroundColor: COLORS.navyBlue,
                borderWidth: 0,
                borderRadius: 20,
                borderSkipped: false,
                barThickness: 18,
                barPercentage: 0.8
            }]
        },
        options: {
            // indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: 'red',
                        fontSize: 12
                    },
                    grid: {
                        color: COLORS.lightGray,
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
                        fontColor: COLORS.navyBlue,
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }

    new Chart(ctx,languageChartConfig);
}