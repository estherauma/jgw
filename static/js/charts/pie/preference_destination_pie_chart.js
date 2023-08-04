function preferenceDestinationPieChart(preferenceDestinationData) {
  
    const labels = preferenceDestinationData["labels"]
    const data = preferenceDestinationData["counts"]
    
    const preferenceDestinationChartConfig = {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'My First Dataset',
                data: data,
                backgroundColor: [
                    COLORS.darkBlue, 
                    COLORS.appleGreen,
                    COLORS.skyBlue,
                    COLORS.navyBlue, 
                    COLORS.black,
                    ...getRandomColorArray(data.length)
                ],
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