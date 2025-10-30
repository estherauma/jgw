function initPreferencesMonthlyUsersChart(preferenceMonthlyUsersChartData, monthlyActiveUserCountData, customContainerId) {
    const containerId = customContainerId || 'preference-monthly-cumulative-users-graph-id';
    const chartDom = document.getElementById(containerId);
    if (!chartDom || !preferenceMonthlyUsersChartData) {
        console.error('Monthly Users Chart: Container or data not found', { containerId, preferenceMonthlyUsersChartData });
        return;
    }

    const chart = echarts.init(chartDom);

    const labels = preferenceMonthlyUsersChartData && preferenceMonthlyUsersChartData.labels ? preferenceMonthlyUsersChartData.labels : [];
    const newUsersCounts = preferenceMonthlyUsersChartData && preferenceMonthlyUsersChartData.counts ? preferenceMonthlyUsersChartData.counts : [];
    const cumulativeCounts = preferenceMonthlyUsersChartData && preferenceMonthlyUsersChartData.cummulative_counts ? preferenceMonthlyUsersChartData.cummulative_counts : [];

    function transformMonthlyActiveUserData(activeData, orderedLabels) {
        if (!Array.isArray(activeData)) return orderedLabels.map(() => 0);
        const monthToCount = new Map(activeData.map(item => [item.month, item.count]));
        return orderedLabels.map(label => monthToCount.get(label) || 0);
    }

    const activeUsersCounts = transformMonthlyActiveUserData(monthlyActiveUserCountData, labels);

    const maxNewUsers = newUsersCounts.length > 0 ? Math.max(...newUsersCounts) : 0;
    const maxNewUsersIndex = newUsersCounts.length > 0 ? newUsersCounts.indexOf(maxNewUsers) : -1;
    const maxActiveUsers = activeUsersCounts.length > 0 ? Math.max(...activeUsersCounts) : 0;
    const maxActiveUsersIndex = activeUsersCounts.length > 0 ? activeUsersCounts.indexOf(maxActiveUsers) : -1;

    const newUsersBarColor = (typeof COLORS !== 'undefined' && COLORS.skyBlue) ? COLORS.skyBlue : '#5B8FF9';
    const newUsersBarBorder = (typeof COLORS !== 'undefined' && COLORS.navyBlue) ? COLORS.navyBlue : '#2B3A67';
    const cumulativeLineColor = (typeof COLORS !== 'undefined' && COLORS.green) ? COLORS.green : '#2E7D32';
    const activeUsersBarBorder = (typeof COLORS !== 'undefined' && COLORS.navyBlue) ? COLORS.navyBlue : '#2B3A67';
    const activeUsersBarColor = (typeof COLORS !== 'undefined' && COLORS.navyBlue) ? COLORS.navyBlue : '#2B3A67';

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            backgroundColor: 'rgba(50, 50, 93, 0.95)',
            borderColor: '#e5e8eb',
            borderWidth: 1,
            textStyle: { color: '#fff', fontSize: 12 }
        },
        legend: {
            data: ['New Users', 'Active Users', 'Cumulative New Users'],
            top: 10,
            textStyle: { color: '#6c757d' }
        },
        grid: {
            left: '4%',
            right: '4%',
            top: 60,
            bottom: 40,
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: labels,
            axisTick: { alignWithLabel: true },
            axisLabel: { color: '#6c757d' },
            axisLine: { lineStyle: { color: '#e5e8eb' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#6c757d' },
            splitLine: { show: true, lineStyle: { color: '#f5f6f8', type: 'dashed' } },
            axisLine: { show: false }
        },
        series: [
            {
                name: 'New Users',
                type: 'bar',
                data: newUsersCounts,
                barGap: '10%',
                itemStyle: {
                    color: newUsersBarColor,
                    borderColor: newUsersBarBorder,
                    borderWidth: 1,
                    borderRadius: [4, 4, 0, 0]
                },
                label: {
                    show: true,
                    position: 'top',
                    color: '#193560',
                    fontWeight: 'bold',
                    fontSize: 12,
                    formatter: function(params) {
                        return params.value;
                    }
                },
                markPoint: maxNewUsersIndex >= 0 ? {
                    data: [
                        {
                            name: 'Max',
                            value: maxNewUsers,
                            xAxis: maxNewUsersIndex,
                            yAxis: maxNewUsers
                        }
                    ],
                    symbol: 'pin',
                    symbolOffset: [0, -25],
                    symbolSize: 50,
                    itemStyle: {
                        color: newUsersBarColor
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: 'Highest: {c}',
                        color: newUsersBarColor,
                        fontWeight: 'bold',
                        fontSize: 11
                    }
                } : null
            },
            {
                name: 'Active Users',
                type: 'bar',
                data: activeUsersCounts,
                itemStyle: {
                    color: activeUsersBarColor,
                    borderColor: activeUsersBarBorder,
                    borderWidth: 1,
                    borderRadius: [4, 4, 0, 0]
                },
                label: {
                    show: true,
                    position: 'top',
                    color: '#193560',
                    fontWeight: 'bold',
                    fontSize: 12,
                    formatter: function(params) {
                        return params.value;
                    }
                },
                markPoint: maxActiveUsersIndex >= 0 ? {
                    data: [
                        {
                            name: 'Max',
                            value: maxActiveUsers,
                            xAxis: maxActiveUsersIndex,
                            yAxis: maxActiveUsers
                        }
                    ],
                    symbol: 'pin',
                    symbolSize: 50,
                    symbolOffset: [0, -35],
                    itemStyle: {
                        color: activeUsersBarColor
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: 'Highest: {c}',
                        color: activeUsersBarColor,
                        fontWeight: 'bold',
                        fontSize: 11
                    }
                } : null
            },
            {
                name: 'Cumulative New Users',
                type: 'line',
                data: cumulativeCounts,
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: { width: 3, color: cumulativeLineColor },
                itemStyle: { color: cumulativeLineColor },
                label: {
                    show: true,
                    position: 'top',
                    color: '#193560',
                    fontWeight: 'bold',
                    fontSize: 12,
                    formatter: function(params) {
                        return params.value;
                    }
                },
                emphasis: { focus: 'series' }
            }
        ]
    };

    chart.setOption(option);
    
    setTimeout(() => chart.resize(), 100);
    window.addEventListener('resize', () => chart.resize());

    return chart;
}


