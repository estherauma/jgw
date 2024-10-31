function chaptersOpenedGraph(chaptersOpenedData) {
    const dataset1 = chaptersOpenedData["chapteropened_all"];
    const dataset2 = chaptersOpenedData["chapteropened_unique"];
    const labels = chaptersOpenedData["labels"];
  
    const chartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Chapter Total Views ",
            data: dataset1,
            backgroundColor: COLORS.navyBlue,
            barThickness: 10,
          },
          {
            label: "Chapter Views by Unique Users",
            data: dataset2,
            backgroundColor: COLORS.skyBlue,
            barThickness: 10,
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
        layout: {
          padding: {
              right: 50,
          },
          margin: {
            bottom: 50,
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
          datalabels: {
            display: false,
         }
        },
      },
      plugins: [ChartDataLabels],
    };
  
    scrollableVerticalBarChart(
      "chapters-opened-graph-id", 
      dataset1, 
      chartConfig
  );
  }
  