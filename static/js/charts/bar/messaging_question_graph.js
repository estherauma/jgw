function messagingQuestionGraph(messagingQuestionData, messagingQuestionCanvasId) {
    const canvas = document.getElementById(messagingQuestionCanvasId);
    if (!canvas) {
        console.error('Canvas element not found:', messagingQuestionCanvasId);
        return;
    }

    const ctx = canvas.getContext('2d');
    const data = messagingQuestionData.counts;
    const labels = messagingQuestionData.labels;

    const minHeight = 400;
    const heightPerLabel = 30; 
    const dynamicHeight = Math.max(minHeight, labels.length * heightPerLabel);

    canvas.style.height = `${dynamicHeight}px`;
    canvas.parentElement.style.height = `${dynamicHeight}px`;

    const messagingChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'RESPONSES',
                data: data,
                backgroundColor: COLORS.navyBlue,
                barThickness: 15,
                borderColor: COLORS.navyBlue,
                borderWidth: 1,
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
                legend: {
                    display: false
                },
                scrollbar: {
                    enabled: true
                },
                datalabels: {
                    anchor: 'end',
                    align: 'right',
                    formatter: (value, context) => {
                        return value;
                    },
                    color: COLORS.navyBlue,
                }
            }
        },
        plugins: [ChartDataLabels],
    };

    new Chart(ctx, messagingChartConfig);
}