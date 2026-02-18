function initMonthlyActiveUsersChart(monthlyActiveUserCountData, customContainerId, chartType) {
    const containerId = customContainerId || 'monthly-active-users-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !monthlyActiveUserCountData) {
        console.error('Monthly Active Users Chart: Container or data not found');
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'bar';
    
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
    
    const totalUsers = userCounts.reduce((sum, count) => sum + count, 0);
    
    const colorPalette = [
        'rgba(50, 50, 93, 0.95)',
        COLORS?.lightGreen || '#6BCB77',
        '#D3DCE6',
        '#B0C4DE',
        '#A8D8EA',
        '#FFD93D',
        '#F38181',
        '#AA96DA',
        '#FCBAD3',
        '#FFB4B4'
    ];
    const colors = months.map((_, index) => colorPalette[index % colorPalette.length]);
    
    let option = {};
    
    if (type === 'pie' || type === 'doughnut') {
        const radius = type === 'doughnut' ? ['40%', '70%'] : ['0%', '70%'];
        option = {
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(50, 50, 93, 0.95)',
                borderColor: '#e5e8eb',
                borderWidth: 1,
                textStyle: {
                    color: '#fff',
                    fontSize: 12
                },
                formatter: function(params) {
                    return params.name + ': ' + params.value + ' (' + params.percent + '%)';
                }
            },
            series: [
                {
                    name: 'Active Users',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: months.map((month, index) => ({
                        name: month,
                        value: userCounts[index]
                    })),
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    label: {
                        show: true,
                        formatter: '{b}: {c} ({d}%)'
                    },
                    labelLine: {
                        show: true
                    },
                    color: colors
                }
            ],
            graphic: type === 'doughnut' ? [
                {
                    type: 'text',
                    left: '50%',
                    top: '50%',
                    style: {
                        text: `Total Users\n${totalUsers}`,
                        textAlign: 'center',
                        fill: '#193560',
                        fontSize: 14,
                        fontWeight: 'bold'
                    },
                    z: 100
                }
            ] : []
        };
    } else {
        const seriesConfig = {
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
        };
        
        option = {
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
            series: [seriesConfig]
        };
    }
    
    myChart.setOption(option);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}
