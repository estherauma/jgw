function preferenceDestinationPieChart(preferenceDestinationData) {
  
    const labels = preferenceDestinationData["labels"]
    const data = preferenceDestinationData["counts"]
    
    const preferenceDestinationChartConfig = {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Users',
                data: data,
                backgroundColor: genericChartColors(data.length),
                barThickness: 15,
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    };
    drawChart('preference-destination-pie-chart-id', data, preferenceDestinationChartConfig);
}