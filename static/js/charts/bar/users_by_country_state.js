function usersByCountryStateChart(usersByCountryStateChartData) {
    const data = usersByCountryStateChartData["counts"];
    const labels = usersByCountryStateChartData["labels"];
  
    const originChartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Preferences",
            data: data,
            backgroundColor: COLORS.appleGreen,
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
      "users-by-country-state-graph-id",
      data,
      originChartConfig
    );
  }
  