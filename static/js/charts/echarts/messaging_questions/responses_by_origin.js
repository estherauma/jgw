/**
 * ECharts: Messaging Questions - Responses by Origin Country
 * Same design pattern as inline_questions/responses_by_origin.js, with fullscreen and chart-type support.
 */
function initMessagingQuestionsResponsesByOriginChart(originData, customContainerId, chartType) {
    const containerId = customContainerId || 'messaging-question-origin-echarts-chart';
    const chartDom = document.getElementById(containerId);

    if (!chartDom || !originData) {
        console.error('Messaging Questions Responses by Origin Chart: Container or data not found', {
            container: containerId,
            data: originData
        });
        return null;
    }

    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }

    const myChart = echarts.init(chartDom);

    const type = chartType || 'doughnut';

    let origins = [];
    let counts = [];

    if (typeof originData === 'object' && originData.labels && originData.counts) {
        origins = [...originData.labels];
        counts = [...originData.counts];
    } else if (Array.isArray(originData)) {
        originData.forEach(item => {
            const origin = item.name || item.origin || item.label || '';
            const count = item.count || item.value || item.y || 0;
            if (origin && count > 0) {
                origins.push(origin);
                counts.push(count);
            }
        });
    } else if (typeof originData === 'object') {
        Object.keys(originData).forEach(key => {
            const count = originData[key];
            if (count && count > 0) {
                origins.push(key);
                counts.push(count);
            }
        });
    }

    if (origins.length === 0 || counts.length === 0) {
        console.warn('No valid data for Messaging Questions Responses by Origin chart');
        return myChart;
    }

    const totalResponses = counts.reduce((sum, count) => sum + count, 0);

    const indexed = origins.map((origin, index) => ({
        origin,
        count: counts[index]
    }));

    indexed.sort((a, b) => b.count - a.count);

    const sortedOrigins = indexed.map(item => item.origin);
    const sortedCounts = indexed.map(item => item.count);

    const numItems = sortedOrigins.length;
    const showScrollbar = numItems > 8;

    const lightGreen = (typeof COLORS !== 'undefined' && COLORS && COLORS.lightGreen) ? COLORS.lightGreen : '#6BCB77';
    const generateColors = (num) => {
        const colors = ['rgba(50, 50, 93, 0.95)', '#8B0000', lightGreen, '#FF8C00', '#00CED1', '#9370DB'];
        const result = [];
        for (let i = 0; i < num; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    };

    const colors = generateColors(sortedOrigins.length);
    const reversedOrigins = [...sortedOrigins].reverse();
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
                    name: 'Responses by Origin',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedOrigins.map((origin, index) => ({
                        name: origin,
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
                        text: `Total\n${totalResponses}`,
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
                data: reversedOrigins,
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
                    name: 'Response Count',
                    type: 'bar',
                    data: reversedCounts.map((count, index) => ({
                        value: count,
                        itemStyle: {
                            color: colors[sortedOrigins.indexOf(reversedOrigins[index])] || '#D3DCE6',
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
