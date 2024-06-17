function usersBySectorsChart(usersBySectorsChartChartData) {
    const data = usersBySectorsChartChartData["counts"];
    const labels = usersBySectorsChartChartData["labels"];
  
    const originChartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Preferences",
            data: data,
            backgroundColor: COLORS.navyBlue,
            barThickness: 15,
          },
        ],
      },
      options: {
        indexAxis: "y",
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
              display: false,
            },
          },
        },
        layout: {
          padding: {
              right: 50,
          }
        },
        maintainAspectRatio: false,
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
  
    scrollableVerticalBarChart(
      "users-by-sector-graph-id",
      data,
      originChartConfig
    );
  }
  