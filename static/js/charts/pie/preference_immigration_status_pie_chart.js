function preferenceImmigrationStatusPieChart(preferenceImmigrationStatusData) {
    const labels = preferenceImmigrationStatusData["labels"]
    const data = preferenceImmigrationStatusData["counts"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Users',
            data: data,
            backgroundColor: genericChartColors(data.length)
        }]
    };
    const config = {
        type: 'pie',
        data: chartData,
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    };

    drawChart('preference-immigration-status-pie-chart-id', data, config);
}
