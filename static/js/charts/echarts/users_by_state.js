function initUsersByStateChart(stateData, customContainerId) {
    const containerId = customContainerId || 'users-by-country-state-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !stateData) {
        console.error('Users by State Chart: Container or data not found', {
            container: containerId,
            data: stateData
        });
        return;
    }
    
    const myChart = echarts.init(chartDom);
    
    let states = [];
    let counts = [];
    
    if (typeof stateData === 'object' && stateData.labels && stateData.counts) {
        states = [...stateData.labels];
        counts = [...stateData.counts];
    } else if (Array.isArray(stateData)) {
        stateData.forEach(item => {
            const state = item.name || item.state || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (state && count > 0) {
                states.push(state);
                counts.push(count);
            }
        });
    } else if (typeof stateData === 'object') {
        Object.keys(stateData).forEach(key => {
            const count = stateData[key];
            if (count && count > 0) {
                states.push(key);
                counts.push(count);
            }
        });
    }
    
    if (states.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by State chart');
        return myChart;
    }
    
    const indexed = states.map((state, index) => ({
        state,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedStates = indexed.map(item => item.state);
    const sortedCounts = indexed.map(item => item.count);
    
    const reversedStates = [...sortedStates].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    
    const numItems = reversedStates.length;
    const showScrollbar = numItems > 8;
    
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
            data: reversedStates,
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
    
    myChart.setOption(option);
    
    setTimeout(() => {
        myChart.resize();
    }, 100);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}

