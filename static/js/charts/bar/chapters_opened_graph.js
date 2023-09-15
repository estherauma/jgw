function chaptersOpenedGraph(chaptersOpenedParams) {
    const data = chaptersOpenedParams["counts"];
    const labels = chaptersOpenedParams["labels"];
  
    const chartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
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
      "chapters-opened-graph-id", 
      data, 
      chartConfig
  );
  }
  