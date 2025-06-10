function reusablePieChart(data, chartId) {
    const labels = data["labels"]
    const counts = data["counts"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Users',
            data: counts,
            backgroundColor: genericChartColors(counts.length)
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

    drawChart(chartId, counts, config);
}