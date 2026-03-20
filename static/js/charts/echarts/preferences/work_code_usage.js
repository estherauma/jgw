function initWorkCodeUsageChart(workCodeUsageParams, customContainerId) {
    try {
        if (typeof echarts === 'undefined') {
            return null;
        }
        
        const containerId = customContainerId || 'organisation-work-code-usage-graph-id';
        const chartDom = document.getElementById(containerId);
        
        if (!chartDom) {
            return null;
        }
        
        if (!workCodeUsageParams || !Array.isArray(workCodeUsageParams) || workCodeUsageParams.length === 0) {
            return null;
        }
        
        const existingChart = echarts.getInstanceByDom(chartDom);
        if (existingChart) {
            existingChart.dispose();
        }
        
        const myChart = echarts.init(chartDom);
        
        const organizations = [...new Set(workCodeUsageParams.map(item => item.organisation_name))].filter(Boolean);
        const accessCodes = [...new Set(workCodeUsageParams.map(item => item.mapped_access_code))].filter(Boolean);
        
        if (organizations.length === 0 || accessCodes.length === 0) {
            return myChart;
        }
        
        const accessCodeColors = accessCodes.reduce((acc, accessCode, index) => {
            if (typeof COLORS !== 'undefined' && Object.keys(COLORS).length > 0) {
                acc[accessCode] = Object.values(COLORS)[index % Object.keys(COLORS).length];
            } else {
                const fallbackColors = [
                    '#5B8FF9', '#5AD8A6', '#FFD93D', '#FF6B6B', '#95E1D3',
                    '#F38181', '#AA96DA', '#FCBAD3', '#6BCB77', '#A8D8EA'
                ];
                acc[accessCode] = fallbackColors[index % fallbackColors.length];
            }
            return acc;
        }, {});

        const organizationTotals = organizations.reduce((acc, org) => {
            acc[org] = workCodeUsageParams
                .filter(item => item.organisation_name === org)
                .reduce((sum, item) => sum + (item.access_code_count || 0), 0);
            return acc;
        }, {});

        const sortedOrganizations = [...organizations].sort((a, b) => {
            return (organizationTotals[b] || 0) - (organizationTotals[a] || 0);
        });
        const chartOrganizations = [...sortedOrganizations].reverse();
        
        const series = accessCodes.map(accessCode => ({
            name: accessCode,
            type: 'bar',
            stack: 'workCode',
            data: chartOrganizations.map(org => {
                const foundItem = workCodeUsageParams.find(
                    item => item.organisation_name === org && item.mapped_access_code === accessCode
                );
                return foundItem ? (foundItem.access_code_count || 0) : 0;
            }),
            itemStyle: {
                color: accessCodeColors[accessCode],
                borderRadius: [0, 4, 4, 0]
            },
            label: {
                show: false,
                position: 'right',
                formatter: function(params) {
                    return params.value > 0 ? params.value : '';
                },
                fontSize: 11,
                color: '#193560',
                fontWeight: 'bold'
            }
        }));
        
        const numItems = chartOrganizations.length;
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
                },
                formatter: function(params) {
                    let result = params[0].name + '<br/>';
                    params.forEach(param => {
                        if (param.value > 0) {
                            result += param.marker + ' ' + param.seriesName + ': ' + param.value + '<br/>';
                        }
                    });
                    const total = params.reduce((sum, param) => sum + (param.value || 0), 0);
                    result += '<strong>Total: ' + total + '</strong>';
                    return result;
                }
            },
            // legend: {
            //     data: accessCodes,
            //     top: 10,
            //     textStyle: {
            //         color: '#6c757d',
            //         fontSize: 12
            //     }
            // },
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
                    end: showScrollbar ? 50 : 100,
                    right: 2,
                    width: 15,  
                    show: showScrollbar,
                    showDetail: false,
                    labelFormatter: function () {
                        return '';
                    },
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
                data: chartOrganizations,
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
            series: series
        };
        
        myChart.setOption(option);
        
        setTimeout(() => {
            try {
                if (myChart && typeof myChart.resize === 'function') {
                    myChart.resize();
                }
            } catch (resizeError) {
            }
        }, 100);
        
  
        const resizeHandler = function() {
            try {
                if (myChart && 
                    typeof myChart.resize === 'function' && 
                    containerId === 'organisation-work-code-usage-graph-id') {
                    myChart.resize();
                }
            } catch (error) {
            }
        };
        
        window.addEventListener('resize', resizeHandler);
        
        myChart._workCodeUsageResizeHandler = resizeHandler;
        
        return myChart;
    } catch (error) {
        return null;
    }
}

