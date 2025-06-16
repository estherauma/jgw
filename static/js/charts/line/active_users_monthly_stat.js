function monthlyActiveUsersChart(monthlyActiveUserCountData) {
    const labels = monthlyActiveUserCountData.map(entry => entry.month);
    const data = monthlyActiveUserCountData.map(entry => entry.count);

      const plugin = {
        beforeInit(chart) {
            const originalFit = chart.legend.fit;
            chart.legend.fit = function fit() {
                originalFit.bind(chart.legend)();
                this.height += 50;
            }
        }
      }
      
      const originChartConfig = {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Active Users per Month",
              data: data,
              backgroundColor: COLORS.skyBlue,
              borderColor: COLORS.navyBlue, 
              borderWidth: 2, 
              fill: 'start' ,
              pointRadius: 5,
              pointHoverRadius: 7
            }
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                drawBorder: false,
                display: false,
                tick: {
                  spacing: 30
                }
              },
            },
          },
          layout: {
            padding: {
                right: 50,
            }
          },
          maintainAspectRatio: true,
          responsive: true,
          plugins: {
            ...externalPluginsConfigDataTables(),
            legend: {
              display: true,
            },
            scrollbar: {
              enabled: true,
            },
          },
        },
        plugins: [ChartDataLabels, plugin],
      };
  
      drawChart("monthly-active-users-graph-id", data, originChartConfig)
  
  }
  