function initUsersByOriginChart(originData, customContainerId, chartType) {
    const containerId = customContainerId || 'preference-origin-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !originData) {
        console.error('Users by Origin Country Chart: Container or data not found', {
            container: containerId,
            data: originData
        });
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'bar';
    
    let countries = [];
    let counts = [];
    
    if (typeof originData === 'object' && originData.labels && originData.counts) {
        countries = [...originData.labels];
        counts = [...originData.counts];
    } else if (Array.isArray(originData)) {
        originData.forEach(item => {
            const country = item.name || item.country || item.origin || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (country && count > 0) {
                countries.push(country);
                counts.push(count);
            }
        });
    } else if (typeof originData === 'object') {    
        Object.keys(originData).forEach(key => {
            const count = originData[key];
            if (count && count > 0) {
                countries.push(key);
                counts.push(count);
            }
        });
    }
    
    if (countries.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Origin Country chart');
        return myChart;
    }
    
    const indexed = countries.map((country, index) => ({
        country,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedCountries = indexed.map(item => item.country);
    const sortedCounts = indexed.map(item => item.count);
    
    const reversedCountries = [...sortedCountries].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    
    const numItems = sortedCountries.length;
    const showScrollbar = numItems > 8;
    
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    const colorPalette = ['rgba(50, 50, 93, 0.95)', COLORS.lightGreen, '#F38181', '#AA96DA', '#FCBAD3', '#FFD93D', '#6BCB77', '#A8D8EA', '#FFB4B4', '#BCE5D0'];
    const colors = sortedCountries.map((_, index) => colorPalette[index % colorPalette.length]);
    
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
                    name: 'Origin Country',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedCountries.map((country, index) => ({
                        name: country,
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
                    end: 85,
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
                data: reversedCountries,
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
                    data: reversedCounts,
                    itemStyle: {
                        color: '#D3DCE6',
                        borderRadius: [0, 4, 4, 0]
                    },
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
