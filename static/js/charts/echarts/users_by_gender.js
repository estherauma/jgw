function initUsersByGenderChart(genderData, customContainerId) {
    const containerId = customContainerId || 'preference-gender-chart-id';
    const chartDom = document.getElementById(containerId);
    
    if (!chartDom || !genderData) {
        console.error('Users by Gender Chart: Container or data not found', {
            container: containerId,
            data: genderData
        });
        return;
    }
    
    // Initialize ECharts instance
    const myChart = echarts.init(chartDom);
    
    // Extract data from the provided dataset
    let genders = [];
    let counts = [];
    
    // Log data for debugging
    console.log('Users by Gender Chart Data:', genderData);
    
    // Handle the specific data structure from Django
    if (typeof genderData === 'object' && genderData.labels && genderData.counts) {
        // Structure: { labels: [...], counts: [...] }
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
    
    console.log('Extracted Gender Data:', { genders, counts });
    
    if (genders.length === 0 || counts.length === 0) {
        console.error('No valid data found for Users by Gender chart');
        return myChart;
    }
    
    // Calculate total users
    const totalUsers = counts.reduce((sum, count) => sum + count, 0);
    
    // Sort by count (descending)
    const indexed = genders.map((gender, index) => ({
        gender,
        count: counts[index]
    }));
    
    indexed.sort((a, b) => b.count - a.count);
    
    const sortedGenders = indexed.map(item => item.gender);
    const sortedCounts = indexed.map(item => item.count);
    
    console.log('Processed Gender Data:', { genders: sortedGenders, counts: sortedCounts });
    
    // Define colors for each gender
    const colorMap = {
        'Male': 'rgba(50, 50, 93, 0.95)',
        'Female': COLORS.lightGreen,
        'Other': '#32CD32',
        'Prefer not to say': '#FF8C00',
        'Not Specified': '#00CED1',
        'Unknown': '#9370DB'
    };
    
    const colors = sortedGenders.map(gender => colorMap[gender] || '#D3DCE6');
    
    // Configuration options for dual chart
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
                // Donut chart on the left
                name: 'User Gender',
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
                data: sortedGenders.map((gender, index) => ({
                    name: gender,
                    value: sortedCounts[index]
                })),
                color: colors
            },
            {
                // Horizontal bar chart on the right
                name: 'User Count',
                type: 'bar',
                xAxisIndex: 0,
                yAxisIndex: 0,
                barWidth: '60%',
                data: sortedCounts.map((count, index) => ({
                    value: count,
                    itemStyle: {
                        color: colors[index],
                        borderRadius : [0, 5, 5, 0]
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
        grid: [
            {
                left: '60%',
                right: '5%',
                top: '10%',
                bottom: '10%',
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
                data: sortedGenders,
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
    
    // Set and render the chart
    myChart.setOption(option);
    
    // Handle window resize
    window.addEventListener('resize', function() {
        myChart.resize();
    });
    
    return myChart;
}

