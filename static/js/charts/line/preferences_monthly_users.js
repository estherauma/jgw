function transformMonthlyActiveUserData(monthlyActiveUserCountData, labels) {
    const monthMap = new Map(monthlyActiveUserCountData.map(item => [item.month, item.count]));
    return labels.map(label => monthMap.get(label) || 0);
}

function preferenceMonthlyUsersChart(preferenceMonthlyUsersChartData, monthlyActiveUserCountData) {
  const labels = preferenceMonthlyUsersChartData["labels"];
  const data = preferenceMonthlyUsersChartData["counts"];
  const cummulativeCounts = preferenceMonthlyUsersChartData["cummulative_counts"];
  const monthlyActiveUsers = transformMonthlyActiveUserData(monthlyActiveUserCountData, labels);

  const plugin = {
    beforeInit(chart) {
        const originalFit = chart.legend.fit;
        chart.legend.fit = function fit() {
            originalFit.bind(chart.legend)();
            this.height += 45;
        }
    }
  }

  const originChartConfig = {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "New Users per Month",
          data: data,
          backgroundColor: COLORS.skyBlue,
          borderColor: COLORS.navyBlue, 
          borderWidth: 2, 
          fill: 'start' ,
          pointRadius: 5,
          pointHoverRadius: 7
        },
        {
          label: "Cumulative New Users",
          data: cummulativeCounts,
          backgroundColor: COLORS.lightGreen,
          borderColor: COLORS.green,
          borderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        },
        {
          label: "Monthly Active Users",
          data: monthlyActiveUsers,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgb(255, 99, 132)',
          borderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        },
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

  drawChart("preference-monthly-cumulative-users-graph-id", data, originChartConfig);
}
