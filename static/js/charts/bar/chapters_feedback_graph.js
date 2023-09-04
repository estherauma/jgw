function chapterFeedBackGraph(feedbackParams) {
  const data = feedbackParams["data"];
  const labels = feedbackParams["labels"];

  const chartConfig = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          data: data["smiles"]["counts"],
          backgroundColor: COLORS.appleGreen,
          barThickness: 15,
        },
        {
            data: data["frowns"]["counts"],
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
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        scrollbar: {
          enabled: true,
        },
      },
    },
  };

  scrollableVerticalBarChart(
    "chapters-feedback-graph-id", 
    [...data["smiles"]["counts"], ...data["frowns"]["counts"]], 
    chartConfig
);
}
