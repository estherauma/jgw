function chapterFeedBackGraph(feedbackParams) {

  const labels = feedbackParams.map((item) => item.chapter_text);
  const frownsData = feedbackParams.map((item) => item.frowns);
  const smilesData = feedbackParams.map((item) => item.smiles);
  const data = [...smilesData, ...frownsData];

  const chartConfig = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Frowns",
          data: frownsData,
          backgroundColor: COLORS.navyBlue,
          barThickness: 15,
        },
        {
          label: "Smiles",
          data: smilesData,
          backgroundColor: COLORS.appleGreen,
          barThickness: 15,
        },
      ],
    },
    options: {
      indexAxis: "y",
      scales: {
        x: { stacked: true },
        y: {
          beginAtZero: true,
          stacked: true,
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
        legend: {
          display: true,
        },
        scrollbar: {
          enabled: true,
        },
      },
    },
  };

  scrollableVerticalBarChart("was-this-helpful-graph-id", data, chartConfig);
}
