function plotChat(key, labels, values) {
  const ctx = document.getElementById("_" + `${key}`).getContext("2d");

  let firstGraphBg = COLORS.skyBlue;
  let secondGraphOneBg = COLORS.appleGreen;

  if (key == "chapter_feedback") {
    firstGraphBg = COLORS.navyBlue;
    secondGraphOneBg = COLORS.appleGreen;
  }

  const chapersAndChapterFeedbackChartConfig = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: values[0].label,
          data: values[0].data,
          backgroundColor: firstGraphBg,
          ...genericBarGraphDatasetConfig,
        },
        {
          label: values[1].label,
          data: values[1].data,
          backgroundColor: secondGraphOneBg,
          ...genericBarGraphDatasetConfig,
        },
      ],
    },
    options: {
      scales: {
        x: {
          beginAtZero: true,
          stacked: true,
          ticks: {
            display: true,
            fontColor: "red",
            fontSize: 12,
          },
          grid: {
            display: false,
          },
          autoSkip: false,
          maxTicksLimit: 5,
        },
        y: {
          beginAtZero: true,
          stacked: true,
          ticks: {
            display: true,
            fontColor: COLORS.navyBlue,
            fontSize: 12,
          },
          grid: {
            drawBorder: false,
            display: false,
          },
          title: {
            display: true,
            text: 'Number of users'
        },
        },
      },
      plugins: {
        legend: {
          display: true,
        },
      },
    },
  };

  new Chart(ctx, chapersAndChapterFeedbackChartConfig);
}
