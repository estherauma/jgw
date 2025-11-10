function initUsersByAgeChart(ageData, customContainerId, chartType) {
    const containerId = customContainerId || 'preference-age-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !ageData) {
        console.error('Users by Age Chart: Container or data not found', {
            container: containerId,
            data: ageData
        });
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'pie';
    
    let ages = [];
    let counts = [];
    
    console.log('Users by Age Chart Data:', ageData);
    
    if (typeof ageData === 'object' && ageData.labels && ageData.counts) {
        ages = [...ageData.labels];
        counts = [...ageData.counts];
    } else if (Array.isArray(ageData)) {
        ageData.forEach(item => {
            const age = item.name || item.age || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (age && count > 0) {
                ages.push(age);
                counts.push(count);
            }
        });
    } else if (typeof ageData === 'object') {
        Object.keys(ageData).forEach(key => {
            const count = ageData[key];
            if (count && count > 0) {
                ages.push(key);
                counts.push(count);
            }
        });
    }
    
    if (ages.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Age chart');
        return myChart;
    }
    
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    
    const indexed = ages.map((age, index) => ({
        age,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedAges = indexed.map(item => item.age);
    const sortedCounts = indexed.map(item => item.count);
    
    console.log('Processed Age Data:', { ages: sortedAges, counts: sortedCounts });

    const colorPalette = [
        'rgba(50, 50, 93, 0.95)',
        COLORS.lightGreen,
        '#F38181',
        '#AA96DA',
        '#FCBAD3',
        '#FFD93D',
        '#6BCB77',
        '#A8D8EA',
        '#FFB4B4',
        '#BCE5D0'
    ];
    
    const colors = sortedAges.map((_, index) => colorPalette[index % colorPalette.length]);
    
    const reversedAges = [...sortedAges].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    const reversedColors = [...colors].reverse();
    
    const numItems = reversedAges.length;
    const showScrollbar = numItems > 8;
    
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
                    name: 'Age Group',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedAges.map((age, index) => ({
                        name: age,
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
                    start: 100,
                    end: 50,
                    right: 2,
                    width: 15,
                    show: showScrollbar,
                    realtime: true,
                    textStyle: {
                        color: '#6c757d'
                    },
                    borderColor: '#e5e8eb',
                    fillerColor: 'rgba(211, 220, 230, 0.3)'
                }
            ],
            yAxis: {
                type: 'category',
                data: reversedAges,
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
                            color: reversedColors[index] || '#D3DCE6',
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


