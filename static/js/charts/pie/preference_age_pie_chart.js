function preferenceAgePieChart(preferenceAgePieChartData) {
    const labels = preferenceAgePieChartData["labels"]
    const data = preferenceAgePieChartData["counts"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'My First Dataset',
            data: data,
            backgroundColor: pieChartColors(data.length)
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

    drawChart('preference-age-graph-id', data, config);
}