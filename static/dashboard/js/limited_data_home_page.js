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