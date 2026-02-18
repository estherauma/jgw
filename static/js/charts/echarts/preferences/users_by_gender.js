function initUsersByGenderChart(genderData, customContainerId, chartType) {
    const containerId = customContainerId || 'preference-gender-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !genderData) {
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'pie';
    
    let genders = [];
    let counts = [];
    
    if (typeof genderData === 'object' && genderData.labels && genderData.counts) {
        genders = [...genderData.labels];
        counts = [...genderData.counts];
    } else if (Array.isArray(genderData)) {
        genderData.forEach(item => {
            const gender = item.name || item.gender || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (gender && count > 0) {
                genders.push(gender);
                counts.push(count);
            }
        });
    } else if (typeof genderData === 'object') {
        Object.keys(genderData).forEach(key => {
            const count = genderData[key];
            if (count && count > 0) {
                genders.push(key);
                counts.push(count);
            }
        });
    }
    
    if (genders.length === 0 || counts.length === 0) {
        return myChart;
    }
    
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    
    const indexed = genders.map((gender, index) => ({
        gender,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedGenders = indexed.map(item => item.gender);
    const sortedCounts = indexed.map(item => item.count);
    
    const colorMap = {
        'Male': 'rgba(50, 50, 93, 0.95)',
        'Female': COLORS.lightGreen,
        'Other': '#32CD32',
        'Prefer not to say': '#FF8C00',
        'Not Specified': '#00CED1',
        'Unknown': '#9370DB'
    };
    
    const colors = sortedGenders.map(gender => colorMap[gender] || '#D3DCE6');
    
    let option = {};
    const reversedGenders = [...sortedGenders].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    const showScrollbar = sortedGenders.length > 8;
    
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
                    name: 'User Gender',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedGenders.map((gender, index) => ({
                        name: gender,
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
                    end: 0,
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
                data: reversedGenders,
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
                            color: colors[sortedGenders.indexOf(reversedGenders[index])] || '#D3DCE6',
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

