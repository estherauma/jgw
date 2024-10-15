function messagingQuestionGraph(inlineQuestionData, inlineQuestionCanvasId) {
    const canvas = document.getElementById(inlineQuestionCanvasId);
    if (!canvas) {
        console.error('Canvas element not found:', inlineQuestionCanvasId);
        return;
    }

    const ctx = canvas.getContext('2d');
    const data = inlineQuestionData.counts;
    const labels = inlineQuestionData.labels;

    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'RESPONSES',
                data: data,
                backgroundColor: COLORS.navyBlue,
                barThickness: 15,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false,
                        display: false
                    },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    }
                },
                x: {
                    position: 'bottom'
                }
            },
            layout: {
                padding: {
                    right: 30,
                    bottom: 20,
                }
            },
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                ...externalPluginsConfigDataTables(),
                legend: {
                    display: false
                },
                scrollbar: {
                    enabled: true
                }
            }
        },
        plugins: [ChartDataLabels],
    };

    const chart = new Chart(ctx, originChartConfig);

    const scrollContainer = document.createElement('div');
    scrollContainer.style.overflowX = 'auto';
    scrollContainer.style.width = '100%';
    canvas.parentNode.insertBefore(scrollContainer, canvas);
    scrollContainer.appendChild(canvas);

    canvas.style.width = `${labels.length * 50}px`;
    canvas.style.height = '100%';

    scrollContainer.addEventListener('scroll', () => {
        chart.update();
    });

    return chart;
}

export default messagingQuestionGraph;