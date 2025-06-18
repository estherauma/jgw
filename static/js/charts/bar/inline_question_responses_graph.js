function inlineQuestionResponsesGraph(responseData) {
  labels = responseData.labels;
  counts = responseData.counts;

  let datasets = [];

  for (let index = 0; index < labels.length; index++) {
    let current_label = labels[index] || "not defined";
    let current_count = counts[index];

    let dataset_part = {};

    for (let cc_i = 0; cc_i < current_count.response_texts.length; cc_i++) {
      dataset_part = {
        label: current_count.response_texts[cc_i],
        data: [current_count.response_counts[cc_i]],
        stack: current_label,
      };
      datasets.push(dataset_part);
    }
  }


  var chartData = {
    labels: labels,
    datasets: [],
  };

  minimumHeight = 50;
  var uniqueLabels = Array.from(new Set(datasets.map((entry) => entry.label)));
  uniqueLabels.forEach((label) => {
    var dataValues = labels.map((stack) => {
      var entry = datasets.find((e) => e.label === label && e.stack === stack);
      return entry ? entry.data[0] : 0;
    });

    // Apply minimum height to small values
    dataValues = dataValues.map((value) =>
      value < minimumHeight ? minimumHeight : value
    );

    chartData.datasets.push({
      label: label,
      data: dataValues,
      // backgroundColor: getRandomColor() // Define your own function to get colors
    });
  });

  const chartConfig = {
    type: "bar",
    data: chartData,
    options: {
      responsive: true,
      interaction: {
        intersect: false,
      },
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
        },
      },
      layout: {
        padding: {
            right: 50,
        }
      },
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

  const canvas = document.getElementById("inline-question-responses-graph");
  canvas.height = 1500; // Set the desired height in pixels

  const ctx = canvas.getContext("2d");
  const chart = new Chart(ctx, chartConfig);

  
}
