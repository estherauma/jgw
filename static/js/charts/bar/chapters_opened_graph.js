function chaptersOpenedGraph(chaptersOpenedParams) {
    const data = chaptersOpenedParams["data"];
    const labels = chaptersOpenedParams["labels"];
  
    const chartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            data: data["views"]["counts"],
            backgroundColor: COLORS.navyBlue,
            barThickness: 15,
          },
          {
              data: data["uniqueUsers"]["counts"],
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
      [...data["views"]["counts"], ...data["uniqueUsers"]["counts"]], 
      chartConfig
  );
  }
  