function phoneNumberClicksByUser(phoneNumberClicksByRoute) {
    const data = phoneNumberClicksByRoute["counts"]
    const labels = phoneNumberClicksByRoute["labels"]
    

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'CLICKS',
                data: data,
                backgroundColor: COLORS.appleGreen,
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

    scrollableVerticalBarChart('phonenumber-clicks-by-user-graph-id', data, originChartConfig);
}