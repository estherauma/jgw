function preferenceMonthlyUsersChart(preferenceMonthlyUsersChartData) {
  const labels = preferenceMonthlyUsersChartData["labels"];
  const data = preferenceMonthlyUsersChartData["counts"];
  const cummulativeCounts = preferenceMonthlyUsersChartData["cummulative_counts"];



    const originChartConfig = {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "New Users per Month",
            data: data,
            backgroundColor: COLORS.skyBlue,
            borderColor: COLORS.navyBlue, 
            borderWidth: 2, 
            fill: 'start' ,
            pointRadius: 5,
            pointHoverRadius: 7
          },
          {
            label: "Cumulative New Users",
            data: cummulativeCounts,
            backgroundColor: COLORS.lightGreen,
            borderColor: COLORS.green,
            borderWidth: 2,
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
        layout: {
          padding: {
              right: 50,
          }
        },
        maintainAspectRatio: true,
        responsive: true,
        plugins: {
          ...externalPluginsConfigDataTables(),
          legend: {
            display: true,
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
