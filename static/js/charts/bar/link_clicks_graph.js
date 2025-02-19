function linkClicksGraph(linkClicksData) {
    const dataset = linkClicksData["link"];
    const labels = linkClicksData["labels"];

    const plugin = {
      beforeInit(chart) {
          const originalFit = chart.legend.fit;
          chart.legend.fit = function fit() {
              originalFit.bind(chart.legend)();
              this.height += 10;
          }
      }
    }

    const chartConfig = {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Link Clicks",
            data: dataset,
            backgroundColor: COLORS.navyBlue,
            barThickness: 10,
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
            display: true,
            color: '#000',
            anchor: 'end',
            align: 'right',
            offset: 10,
            formatter: function(value) {
              return value;
            }
          }
        },
      },
      plugins: [ChartDataLabels, plugin],
    };
  
    scrollableVerticalBarChart(
      "link-clicks-graph-id", 
      dataset, 
      chartConfig
    );
}