const data = [
    { lang: 'English', count: 10 },
    { lang: 'Russian', count: 20 },
    { lang: 'Nepali', count: 15 },
    { lang: 'Ukranian', count: 25 },
    { lang: 'Romanian', count: 22 },
    { lang: 'Bulgarian', count: 30 },
    { lang: 'Serbian', count: 28 },
];
new Chart(
    document.getElementById('acquisitions'),
    {
        type: 'pie',
        data: {
            labels: data.map(row => row.lang),
            datasets: [
                {
                    label: 'Language',
                    data: data.map(row => row.count),
                    backgroundColor: ["red", "blue", "green", "purple", "maroon", "grey", 'orange'],
                }
            ]
        },

        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },

            }

        }
    }
);


function uniqueAndReturningUsersGraph({ returning_data, unique_data, labels }) {
    let options = {
        series: [
            {
                name: 'Returning users',
                data: returning_data,
            },
            {
                name: 'Unique users',
                data: unique_data,
            }],
        chart: {
            type: 'bar',
            height: 500
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: "55%",
                barHeight: 50,
                endingShape: 'rounded'
            }
        },
        title: {
            text: "Unique and Returning users",
            style: {
                fontSize: '18px',
                fontWeight: '400',
                fontFamily: undefined,
                color: '#343A40'
            },
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        xaxis: {
            categories: labels,
        },
        fill: {
            opacity: 1
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val
                }
            }
        }
    };

    let chart = new ApexCharts(document.querySelector("#unique-and-returning-users"), options);
    chart.render();
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

