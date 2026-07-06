function initUsersByLanguageChart(languageData, customContainerId, chartType) {
    const containerId = customContainerId || 'preference-language-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !languageData) {
        console.error('Users by Language Chart: Container or data not found', {
            container: containerId,
            data: languageData
        });
        return;
    }
    
    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    
    const type = chartType || 'bar';
    
    let languages = [];
    let counts = [];
    
    if (typeof languageData === 'object' && languageData.labels && languageData.counts) {
        languages = [...languageData.labels];
        counts = [...languageData.counts];
    } else if (Array.isArray(languageData)) {
        languageData.forEach(item => {
            const language = item.name || item.language || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (language && count > 0) {
                languages.push(language);
                counts.push(count);
            }
        });
    } else if (typeof languageData === 'object') {
        Object.keys(languageData).forEach(key => {
            const count = languageData[key];
            if (count && count > 0) {
                languages.push(key);
                counts.push(count);
            }
        });
    }
    
    if (languages.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Language chart');
        return myChart;
    }
    
    const indexed = languages.map((language, index) => ({
        language,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedLanguages = indexed.map(item => item.language);
    const sortedCounts = indexed.map(item => item.count);
    
    const reversedLanguages = [...sortedLanguages].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    
    const numItems = reversedLanguages.length;
    const showScrollbar = numItems > 8;
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    const colorPalette = ['rgba(50, 50, 93, 0.95)', COLORS.lightGreen, '#F38181', '#AA96DA', '#FCBAD3', '#FFD93D', '#6BCB77', '#A8D8EA', '#FFB4B4', '#BCE5D0'];
    const colors = sortedLanguages.map((_, index) => colorPalette[index % colorPalette.length]);
    
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
                    name: 'Language',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedLanguages.map((language, index) => ({
                        name: language,
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
                data: reversedLanguages,
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
                        borderRadius: [4, 4, 0, 0]
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
                        fontSize: 12
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

