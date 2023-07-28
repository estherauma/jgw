function preferenceDestinationChart(preferenceDestinationData) {
  
    const labels = preferenceDestinationData["labels"]
    const data = preferenceDestinationData["data"]
    
    const preferenceDestinationChartConfig = {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'My First Dataset',
                data: data,
                backgroundColor: [COLORS.darkBlue, COLORS.appleGreen,COLORS.skyBlue,COLORS.navyBlue, COLORS.black],
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
    drawChart('preference_destination_graphcard', data, preferenceDestinationChartConfig);
}