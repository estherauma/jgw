function preferenceGenderPieChart(preferenceGenderGraphData) {
    const labels = preferenceGenderGraphData["labels"]
    const data = preferenceGenderGraphData["counts"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'My First Dataset',
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

    drawChart('preference-gender-pie-chart-id', data, config);
}