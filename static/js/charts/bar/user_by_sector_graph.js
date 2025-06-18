function usersBySectorsChart(chartData, chartId = "users-by-sector-graph-id", label = "Users") {
    const data = chartData["counts"];
    const labels = chartData["labels"];
  
    const chartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: label,
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
      chartId,
      data,
      chartConfig
    );
  }
  