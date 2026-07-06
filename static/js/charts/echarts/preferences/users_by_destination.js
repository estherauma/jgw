function initUsersByDestinationChart(destinationData, customContainerId, chartType) {
    const containerId = customContainerId || 'preference-destination-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !destinationData) {
        console.error('Users by Destination Country Chart: Container or data not found', {
            container: containerId,
            data: destinationData
        });
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'doughnut';
    
    let destinations = [];
    let counts = [];
    
    if (typeof destinationData === 'object' && destinationData.labels && destinationData.counts) {
        destinations = [...destinationData.labels];
        counts = [...destinationData.counts];
    } else if (Array.isArray(destinationData)) {
        destinationData.forEach(item => {
            const destination = item.name || item.destination || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (destination && count > 0) {
                destinations.push(destination);
                counts.push(count);
            }
        });
    } else if (typeof destinationData === 'object') {
        Object.keys(destinationData).forEach(key => {
            const count = destinationData[key];
            if (count && count > 0) {
                destinations.push(key);
                counts.push(count);
            }
        });
    }
    
    if (destinations.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Destination Country chart');
        return myChart;
    }
    
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    
    const indexed = destinations.map((destination, index) => ({
        destination,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedDestinations = indexed.map(item => item.destination);
    const sortedCounts = indexed.map(item => item.count);
    
    const numItems = sortedDestinations.length;
    const showScrollbar = numItems > 8;
    
    const generateColors = (num) => {
        const colors = ['rgba(50, 50, 93, 0.95)', '#8B0000', COLORS.lightGreen, '#FF8C00', '#00CED1', '#9370DB'];
        const result = [];
        for (let i = 0; i < num; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    };
    
    const colors = generateColors(sortedDestinations.length);
    const reversedDestinations = [...sortedDestinations].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    
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
                    name: 'User Destination',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedDestinations.map((destination, index) => ({
                        name: destination,
                        value: sortedCounts[index]
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
                    color: colors
                }
            ],
            graphic: [
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
            ]
        };
    } else {
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
                left: '5%',
                right: '5%',
                bottom: '0%',
                top: '5%',
                containLabel: true
            },
            dataZoom: [
                {
                    type: 'slider',
                    yAxisIndex: 0,
                    filterMode: 'none',
                    start: showScrollbar ? 100 : 0,
                    end: showScrollbar ? 50 : 100,
                    right: 2,
                    width: 15,
                    show: showScrollbar,
                    realtime: true,
                    showDetail: false,
                    labelFormatter: function () {
                        return '';
                    },
                    textStyle: {
                        color: '#6c757d'
                    },
                    borderColor: '#e5e8eb',
                    fillerColor: 'rgba(211, 220, 230, 0.3)'
                }
            ],
            yAxis: {
                type: 'category',
                data: reversedDestinations,
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
            xAxis: {
                type: 'value',
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
                    name: 'User Count',
                    type: 'bar',
                    data: reversedCounts.map((count, index) => ({
                        value: count,
                        itemStyle: {
                            color: colors[sortedDestinations.indexOf(reversedDestinations[index])] || '#D3DCE6',
                            borderRadius: [0, 4, 4, 0]
                        }
                    })),
                    emphasis: {
                        itemStyle: {
                            color: '#B0C4DE'
                        }
                    },
                    label: {
                        show: true,
                        position: 'right',
                        color: '#193560',
                        fontWeight: 'bold',
                        fontSize: 12,
                        formatter: function(params) {
                            return params.value;
                        }
                    }
                }
            ]
        };
    }
    
    myChart.setOption(option);
    
    setTimeout(() => {
        myChart.resize();
    }, 100);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}

