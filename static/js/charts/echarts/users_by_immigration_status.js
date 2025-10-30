function initUsersByImmigrationStatusChart(immigrationData, customContainerId) {
    const containerId = customContainerId || 'preference-immigration-status-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !immigrationData) {
        console.error('Users by Immigration Status Chart: Container or data not found', {
            container: containerId,
            data: immigrationData
        });
        return;
    }

    const myChart = echarts.init(chartDom);
    
    let statuses = [];
    let counts = [];
    
    console.log('Users by Immigration Status Chart Data:', immigrationData);
    
    if (typeof immigrationData === 'object' && immigrationData.labels && immigrationData.counts) {
        statuses = [...immigrationData.labels];
        counts = [...immigrationData.counts];
    } else if (Array.isArray(immigrationData)) {
        immigrationData.forEach(item => {
            const status = item.name || item.status || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (status && count > 0) {
                statuses.push(status);
                counts.push(count);
            }
        });
    } else if (typeof immigrationData === 'object') {
        Object.keys(immigrationData).forEach(key => {
            const count = immigrationData[key];
            if (count && count > 0) {
                statuses.push(key);
                counts.push(count);
            }
        });
    }
    
    console.log('Extracted Immigration Data:', { statuses, counts });
    
    if (statuses.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Immigration Status chart');
        return myChart;
    }
    
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    
    const indexed = statuses.map((status, index) => ({
        status,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedStatuses = indexed.map(item => item.status);
    const sortedCounts = indexed.map(item => item.count);
    
    console.log('Processed Immigration Status Data:', { statuses: sortedStatuses, counts: sortedCounts });
    
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
    
    const colors = sortedStatuses.map((_, index) => colorPalette[index % colorPalette.length]);
    
    const reversedStatuses = [...sortedStatuses].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    const reversedColors = [...colors].reverse();
    
    const numItems = reversedStatuses.length;
    const showScrollbar = numItems > 8;
    
    const option = {
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
                name: 'Immigration Status',
                type: 'pie',
                center: ['25%', '50%'],
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 5,
                    borderRadius: 10
                },
                label: {
                    show: false
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 12,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: sortedStatuses.map((status, index) => ({
                    name: status,
                    value: sortedCounts[index]
                })),
                color: colors
            },
            {
                name: 'User Count',
                type: 'bar',
                xAxisIndex: 0,
                yAxisIndex: 0,
                barWidth: '50%',
                data: reversedCounts.map((count, index) => ({
                    value: count,
                    itemStyle: {
                        color: reversedColors[index],
                        borderRadius: [0, 5, 5, 0]
                    }
                })),
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
        ],
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
        grid: [
            {
                left: '60%',
                right: '0%',
                top: '5%',
                bottom: '5%',
                containLabel: false
            }
        ],
        xAxis: [
            {
                gridIndex: 0,
                type: 'value',
                position: 'top',
                axisLine: {
                    show: false
                },
                axisLabel: {
                    show: false
                },
                splitLine: {
                    show: true,
                    lineStyle: {
                        color: '#f5f6f8',
                        type: 'dashed'
                    }
                }
            }
        ],
        yAxis: [
            {
                gridIndex: 0,
                type: 'category',
                data: reversedStatuses,
                axisLine: {
                    show: false
                },
                axisLabel: {
                    color: '#6c757d',
                    fontSize: 12
                }
            }
        ],
        graphic: [
            {
                type: 'text',
                left: '25%',
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
    
        myChart.setOption(option);
    
    setTimeout(() => {
        myChart.resize();
    }, 100);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}


