function chapterFeedBackGraph(feedbackParams) {
  feedbackParams.map( (feedbackParam) => {
    const question = feedbackParam["question"]
    const data = feedbackParam["data"]

    if (question === "tellUsMore") {
      plotGraph("tell-us-more-graph-id", data, COLORS.skyBlue)
    }
    if (question === "wasThisHelpful") {
      plotGraph("was-this-helpful-graph-id", data)
    }
  })
}

function plotGraph(id, feedbackParam, backgroundColor = COLORS.appleGreen) {
  const data = feedbackParam["counts"];
  const labels = feedbackParam["labels"];

  const chartConfig = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: backgroundColor,
          barThickness: 15,
        }
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

  scrollableVerticalBarChart( id, data, chartConfig );
}
