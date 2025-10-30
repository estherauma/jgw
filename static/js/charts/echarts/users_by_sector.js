function initUsersBySectorChart(sectorData, customContainerId) {
    const containerId = customContainerId || 'users-by-sector-graph-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !sectorData) {
        console.error('Users by Sector Chart: Container or data not found', {
            container: containerId,
            data: sectorData
        });
        return;
    }
    
    const myChart = echarts.init(chartDom);
    
    let sectors = [];
    let counts = [];
    
    console.log('Users by Sector Chart Data:', sectorData);
    
    if (typeof sectorData === 'object' && sectorData.labels && sectorData.counts) {
        sectors = [...sectorData.labels];
        counts = [...sectorData.counts];
    } else if (Array.isArray(sectorData)) {
        sectorData.forEach(item => {
            const sector = item.name || item.sector || item.label || '';
            const count = item.count || item.value || item.y || 0;
            
            if (sector && count > 0) {
                sectors.push(sector);
                counts.push(count);
            }
        });
    } else if (typeof sectorData === 'object') {
        Object.keys(sectorData).forEach(key => {
            const count = sectorData[key];
            if (count && count > 0) {
                sectors.push(key);
                counts.push(count);
            }
        });
    }
    
    console.log('Extracted Sector Data:', { sectors, counts });
    
    if (sectors.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Sector chart');
        return myChart;
    }
    
    const indexed = sectors.map((sector, index) => ({
        sector,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedSectors = indexed.map(item => item.sector);
    const sortedCounts = indexed.map(item => item.count);
    
    console.log('Processed Sector Data (sorted):', { sectors: sortedSectors, counts: sortedCounts });
    
    const reversedSectors = [...sortedSectors].reverse();
    const reversedCounts = [...sortedCounts].reverse();
    
    console.log('Reversed Sector Data (for display):', { sectors: reversedSectors, counts: reversedCounts });
    
    const numItems = sortedSectors.length;
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
            data: reversedSectors,
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
    
    myChart.setOption(option);
    
    setTimeout(() => {
        myChart.resize();
    }, 100);
    
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}
