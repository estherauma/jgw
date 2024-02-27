function preferenceMonthlyUsersChart(preferenceMonthlyUsersChartData) {
  const labels = preferenceMonthlyUsersChartData["labels"];
  const data = preferenceMonthlyUsersChartData["counts"];

    const originChartConfig = {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Users",
            data: data,
            backgroundColor: COLORS.skyBlue,
            borderColor: COLORS.navyBlue, 
            borderWidth: 2, 
            fill: 'start' ,
            pointRadius: 5,
            pointHoverRadius: 7
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
              display: false,
              tick: {
                spacing: 30
              }
            },
          },
        },
        maintainAspectRatio: true,
        responsive: true,
        plugins: {
          ...externalPluginsConfigDataTables(),
          legend: {
            display: false,
          },
          scrollbar: {
            enabled: true,
          },
        },
      },
      plugins: [ChartDataLabels],
    };

    drawChart("preference-monthly-cumulative-users-graph-id", data, originChartConfig)

}
