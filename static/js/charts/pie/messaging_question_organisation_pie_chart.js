function messagingQustionOrganisationPieChart(orgChartData) {
    const labels = orgChartData["labels"]
    const data = orgChartData["counts"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Messaging Questions Responses',
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

    drawChart('messaging-question-organisation-pie-chart-id', data, config);
}