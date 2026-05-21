/**
 * ECharts: Messaging Questions - Responses by Organisation
 * Same design pattern as inline_questions/responses_by_origin.js, with fullscreen and chart-type support.
 */
function initMessagingQuestionsResponsesByOrganisationChart(organisationData, customContainerId, chartType) {
    const containerId = customContainerId || 'messaging-question-organisation-echarts-chart';
    const chartDom = document.getElementById(containerId);

    if (!chartDom || !organisationData) {
        console.error('Messaging Questions Responses by Organisation Chart: Container or data not found', {
            container: containerId,
            data: organisationData
        });
        return null;
    }

    const existingChart = echarts.getInstanceByDom(chartDom);
    if (existingChart) {
        existingChart.dispose();
    }

    const myChart = echarts.init(chartDom);

    const type = chartType || 'doughnut';

    let organisations = [];
    let counts = [];
    let noDataMessage = 'No data available';

    if (typeof organisationData === 'object' && organisationData.labels && organisationData.counts) {
        organisations = [...organisationData.labels];
        counts = [...organisationData.counts];
        if (organisationData.message) {
            noDataMessage = organisationData.message;
        }
    } else if (Array.isArray(organisationData)) {
        organisationData.forEach(item => {
            const org = item.name || item.organisation || item.label || '';
            const count = item.count || item.value || item.y || 0;
            if (org && count > 0) {
                organisations.push(org);
                counts.push(count);
            }
        });
    } else if (typeof organisationData === 'object') {
        Object.keys(organisationData).forEach(key => {
            const count = organisationData[key];
            if (count && count > 0) {
                organisations.push(key);
                counts.push(count);
            }
        });
    }

    if (organisations.length === 0 || counts.length === 0) {
        console.warn('No valid data for Messaging Questions Responses by Organisation chart');
        myChart.setOption({
            title: {
                text: noDataMessage,
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#6c757d',
                    fontSize: 14,
                    fontWeight: 'normal'
                }
            },
            xAxis: { show: false },
            yAxis: { show: false },
            series: []
        });
        return myChart;
    }

    const totalResponses = counts.reduce((sum, count) => sum + count, 0);

    const indexed = organisations.map((org, index) => ({
        organisation: org,
        count: counts[index]
    }));

    indexed.sort((a, b) => b.count - a.count);

    const sortedOrganisations = indexed.map(item => item.organisation);
    const sortedCounts = indexed.map(item => item.count);

    const numItems = sortedOrganisations.length;
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

    const colors = generateColors(sortedOrganisations.length);
    const reversedOrganisations = [...sortedOrganisations].reverse();
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
                    name: 'Responses by Organisation',
                    type: 'pie',
                    radius: radius,
                    center: ['50%', '50%'],
                    data: sortedOrganisations.map((org, index) => ({
                        name: org,
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
                data: reversedOrganisations,
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
                            color: colors[sortedOrganisations.indexOf(reversedOrganisations[index])] || '#D3DCE6',
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
