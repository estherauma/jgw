function genericBarChart(key, values) {
    graphDiv = document.getElementById(`${key}_graphcard`)
    
    let canvas = document.createElement('canvas')
    canvas.setAttribute('id', `_${key}`)
    canvas.setAttribute('class', "chartContainer")
    graphDiv.appendChild(canvas)

    const chartObject = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: removeBrTags(values.labels),
            datasets: [
                {
                    label: key,
                    data: values.data,
                    backgroundColor: COLORS.appleGreen,
                    borderWidth: 0,
                    borderRadius: 20,
                    borderSkipped: false,
                    barThickness: 18,
                    barPercentage: 0.8
                },
            ],
        },
        options: {
            indexAxis: 'y',
            hover: { mode: null },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false,
                    text: key,
                    font: {
                        size: 20,
                        weight: '400',
                        lineHeight: 1.2,
                        textAlign: 'left',
                    },
                    padding: { top: 20, left: 0, right: 0, bottom: 20 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            maintainAspectRatio: false,
            responsive: true,
        },
        plugins: {
            scrollbar: {
                enabled: true
            }
        }
    });

    const totalChart = chartObject.config.data.labels.length
    let totalHeight;

    /** 
        if the number of bars are > 25, add generic-chart-box class to currentChartBox
        to make it scrollable instead of a very long chart
    **/
    let currentChartBox = document.querySelector(`.${key}-chart-box`)

    if (totalChart <= 10) {
        totalHeight = `${totalChart * 50}px`
    } else if (totalChart > 28) {
        totalHeight = `${totalChart * 28}px`
        currentChartBox.classList.add('generic-chart-box')
    } else {
        totalHeight = `${totalChart * 28}px`
    }
    graphDiv.style.height = totalHeight;
}