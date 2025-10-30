function initUsersByDestinationChart(destinationData, customContainerId) {
    const containerId = customContainerId || 'preference-destination-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !destinationData) {
        console.error('Users by Destination Country Chart: Container or data not found', {
            container: containerId,
            data: destinationData
        });
        return;
    }
    
    const myChart = echarts.init(chartDom);
    
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
                name: 'User Destination',
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
                data: sortedDestinations.map((destination, index) => ({
                    name: destination,
                    value: sortedCounts[index]
                })),
                color: colors
            },
            {
                name: 'User Count',
                type: 'bar',
                xAxisIndex: 0,
                yAxisIndex: 0,
                barWidth: '60%',
                data: sortedCounts.map((count, index) => ({
                    value: count,
                    itemStyle: {
                        color: colors[index]
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
        grid: [
            {
                left: '60%',
                right: '5%',
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
                data: sortedDestinations,
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

