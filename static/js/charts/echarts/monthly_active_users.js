function initMonthlyActiveUsersChart(monthlyActiveUserCountData, customContainerId) {
    const containerId = customContainerId || 'monthly-active-users-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !monthlyActiveUserCountData) {
        console.error('Monthly Active Users Chart: Container or data not found');
        return;
    }
    
    const myChart = echarts.init(chartDom);
    
    const months = [];
    const userCounts = [];
    
    if (Array.isArray(monthlyActiveUserCountData)) {
        monthlyActiveUserCountData.forEach(item => {
            months.push(item.month || item.Month);
            userCounts.push(item.count || item.Count || 0);
        });
    } else if (typeof monthlyActiveUserCountData === 'object') {
        Object.keys(monthlyActiveUserCountData).forEach(key => {
            months.push(key);
            userCounts.push(monthlyActiveUserCountData[key]);
        });
    }
    
    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            backgroundColor: 'rgba(50, 50, 93, 0.95)',
            borderColor: '#e5e8eb',
            borderWidth: 1,
            textStyle: {
                color: '#fff',
                fontSize: 12
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: months,
            axisLine: {
                show: true,
                lineStyle: {
                    color: '#e5e8eb'
                }
            },
            axisLabel: {
                color: '#6c757d',
                fontSize: 12
            },
            splitLine: {
                show: false
            }
        },
        yAxis: {
            axisLine: {
                show: false
            },
            axisLabel: {
                color: '#6c757d',
                fontSize: 12
            },
            splitLine: {
                show: true,
                lineStyle: {
                    color: '#f5f6f8',
                    type: 'dashed'
                }
            }
        },
        series: [
            {
                name: 'Active Users',
                type: 'bar',
                data: userCounts,
                itemStyle: {
                    color: '#D3DCE6',
                    borderRadius: [4, 4, 0, 0]
                },
                emphasis: {
                    itemStyle: {
                        color: '#B0C4DE'
                    }
                },
                label: {
                    show: true,
                    position: 'top',
                    color: '#193560',
                    fontWeight: 'bold',
                    fontSize: 12
                }
            }
        ]
    };
    
    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}
