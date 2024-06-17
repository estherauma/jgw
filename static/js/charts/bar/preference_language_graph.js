function preferenceLanguageGraph(langaugeData) {
  const data = langaugeData["counts"];
  const labels = langaugeData["labels"];

  const languageChartConfig = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "PREFERENCES",
          data: data,
          backgroundColor: COLORS.skyBlue,
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
    "preference-language-graph-id",
    data,
    languageChartConfig
  );
}
