function workCodeUsageStackBar(workCodeUsageParams) {
    const organizations = [...new Set(workCodeUsageParams.map(item => item.organisation_name))];
    const accessCodes = [...new Set(workCodeUsageParams.map(item => item.mapped_access_code))];
    
    const accessCodeColors = accessCodes.reduce((acc, accessCode, index) => {
        acc[accessCode] = Object.values(COLORS)[index % Object.keys(COLORS).length];
        return acc;
    }, {});

    const datasets = accessCodes.map(accessCode => ({
        label: accessCode,
        data: organizations.map(org => {
            const foundItem = workCodeUsageParams.find(item => item.organisation_name === org && item.access_code === accessCode);
            return foundItem ? foundItem.access_code_count : 0;
        }),
        backgroundColor: accessCodeColors[accessCode]
    }));

    const chartConfig = {
      type: "bar",
      data: {
        labels: organizations,
        datasets: datasets,
      },
      options: {
        indexAxis: "y",
        scales: {
          x: { stacked: true },
          y: {
            beginAtZero: true,
            stacked: true,
            grid: {
              drawBorder: false,
              display: false,
            },
          },
        },
        layout: {
          padding: {
              right: 50,
          }
        },
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
          ...externalPluginsConfigDataTables(),
          legend: {
            display: true,
          },
          scrollbar: {
            enabled: false,
          },
        },
      },
    };
  
    scrollableVerticalBarChart("organisation-work-code-usage-graph-id", workCodeUsageParams, chartConfig);
}
