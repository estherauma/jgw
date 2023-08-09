function inlineQustionOrganisationPieChart(orgChartData) {
    const labels = orgChartData["labels"]
    const data = orgChartData["counts"]
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

    drawChart('inline-question-organisation-pie-chart-id', data, config);
}