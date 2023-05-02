
const export_button = document.querySelector('#exportParticipation')
const export_url = export_button.attributes.getNamedItem("export-url").value;
const export_button_1 = document.querySelector('#exportAnswersBreakdown')
const export_url_1 = export_button_1.attributes.getNamedItem("export-url").value;
const end_date = document.querySelector('#end_date')
const factoryFarm_input = document.querySelector('#factory_farm')
const filter_form = document.querySelector('#filter_form')
const origin_input = document.querySelector('#origin')
const start_date = document.querySelector('#start_date')

function toggleElementDisplay(flag, selector) {
    const element = document.querySelector(selector)
    if (flag === true) {
        element.style.display = 'block'
    } else if (flag === false) {
        element.style.display = 'none'
    }
}

function setFormErrors(errorObject) {
    for (const [key, value] of Object.entries(errorObject)) {
        const element = document.querySelector(`#${key}-errors`)
        element.textContent = value[0]
    }
}

function clearFormErrors() {
    const errorMessages = document.querySelectorAll('[id$="-errors"]')
    for (i in errorMessages) {
        i.textContent = ''
    }
}

function getOriginOptions() {
    const destination_input = document.querySelector('#destination')
    const url = filter_form.attributes.getNamedItem("data-origins-url").value;
    const dest_country = destination_input.value;
    const origin_country = origin_input.value;
    if (dest_country) {
        const filters = new URLSearchParams({ 'destination': dest_country })
        fetch(`${url}?${filters}`, { method: 'GET' })
            .then(response => {
                result = response.json()
                status_code = response.status;
                if (status_code != 200) {
                    console.log('Error processing next field options')
                    return false;
                }
                return result
            })
            .then(data => {
                options = ``
                Object.entries(data).map(function ([k, v]) {
                    if (k === origin_country) {
                        options += `<option value="${k}" selected>${v}</option>`
                    }
                    options += `<option value="${k}">${v}</option>`
                })
                origin_input.innerHTML = options;
                filterData()
            })
            .catch(error => {
                console.log(error)
            })
    }
}

function getFactoryOptions() {
    const url = filter_form.attributes.getNamedItem("data-factories-url").value;
    const destination_input = document.querySelector('#destination')
    const schemeName_input = document.querySelector('#scheme_name')
    const schemeName = schemeName_input.value;
    const factoryFarm = factoryFarm_input.value;
    const dest_country = destination_input.value;
    const origin_country = origin_input.value;

    if (dest_country && origin_country && schemeName && !factoryFarm) {
        const filters = new URLSearchParams({
            'destination': dest_country,
            'origin': origin_country,
            'scheme_name': schemeName
        })
        fetch(`${url}?${filters}`, { method: 'GET' })
            .then(response => {
                result = response.json()
                status_code = response.status;
                if (status_code != 200) {
                    console.log('Error processing next field options')
                    return false;
                }
                return result
            })
            .then(data => {
                options = ``
                Object.entries(data).map(function ([k, v]) {
                    if (k === factoryFarm) {
                        options += `<option value="${k}" selected>${v}</option>`
                    }
                    options += `<option value="${k}">${v}</option>`
                })
                factoryFarm_input.innerHTML = options;
                filterData()
            })
            .catch(error => {
                console.log(error)
            })
    }
}

function autosubmit() {
    clearCharts()
    document.getElementById('time_range').value = '';
    filterData()
}

function filterData() {
    clearCharts()

    const url = filter_form.attributes.getNamedItem("submit-url").value;
    const formData = new FormData(filter_form);

    let chartData = {};
    toggleElementDisplay(false, '#chart-area')
    toggleElementDisplay(true, '#loader')
    toggleElementDisplay(false, '#no-results')
    clearFormErrors()
    
    fetch(url, { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if ('form_errors' in data) {
                setFormErrors(data.form_errors)
            }
            else {
                chartData = data['chart_data']
                
                if (Object.keys(chartData).length === 0) {
                    toggleElementDisplay(true, '#no-results')
                } else {
                    responseCountValue = data['response_count']
                    const responseCountElement = document.querySelector('#response-count')
                    responseCountElement.textContent = responseCountValue
                    plotCharts(chartData)
                    toggleElementDisplay(true, '#chart-area')
                }
            }
            
            const filterStateData = data["filter_state"]
            buildFilterStateAlert('inline-question', filterStateData)
        })
        .catch(error => {
            console.log(error)
        })
        .finally(() => toggleElementDisplay(false, '#loader'))

}

function exportToExcel(url) {
    const formData = new FormData(filter_form);
    toggleElementDisplay(false, '#chart-area')
    toggleElementDisplay(false, '#no-results')
    toggleElementDisplay(true, '#loader')
    fetch(url, { method: 'POST', body: formData })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText)
            } else {
                const header = response.headers.get('Content-Disposition');
                const parts = header.split(';');
                filename = parts[1].split('=')[1].replaceAll("\"", "");
                return response.blob();
            }
        })
        .then(blob => {
            if (blob != null) {
                const a = document.createElement('a');
                a.href = window.URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        })
        .catch(error => {
            console.log(error)
        })
        .finally(() => {
            toggleElementDisplay(true, '#chart-area')
            toggleElementDisplay(false, '#loader')
        })
}

function removeBrTags(list) {
    const newList = list.map(item => item.replace(/<br\/><br\/>/g, ''));
    return newList;
}

function plotCharts(chartData) {
    if (chartData) {
        let chartDataKeys = Object.keys(chartData)

        chartDataKeys.map(chartDataKey => {
            if (chartDataKey === "organisation") {
                organisationChart(chartData['organisation'])
            }

            if (chartDataKey === "destination") {
                destinationChart(chartData['destination'])
            }

            if (chartDataKey === "origin") {
                originChart(chartData['origin'])
            }

            if (chartDataKey === "language") {
                languageChart(chartData['language'])
            }


            if (chartDataKey === "question") {
                genericBarChart(chartDataKey, chartData['question'])
            }
        })
    }
}


function organisationChart(organisationData) {
    const data = organisationData["data"]
    const organisationCleanedLabels = organisationData["labels"].map(org => { 
        return org.replace("Seasonal Worker Scheme - ", "").replace("Seasonal  Worker Scheme - ", "")
    })
    const organisationChartData = {
        labels: organisationCleanedLabels,
        datasets: [{
          label: 'Responses',
          data: data,
          backgroundColor: [
            COLORS.mediumBlue,
            COLORS.skyBlue,
            COLORS.navyBlue,
            COLORS.appleGreen,
          ],
          hoverOffset: 4
        }]
      };
      const organisationChartConfig = {
        type: 'doughnut',
        data: organisationChartData,
        options: {
            plugins: {
                legend: {
                    display: true,
                }
            }
        }
      };

    drawChart('organisation_graph', data, organisationChartConfig)
}

function genericBarChart(key, values) {
    graphDiv = document.getElementById(`${key}_graphcard`)
    
    let canvas = document.createElement('canvas')
    canvas.setAttribute('id', `_${key}`)
    canvas.setAttribute('class', "chartContainer")
    graphDiv.appendChild(canvas)

    const data = values.data

    const chartConfig = {
        type: "bar",
        data: {
            labels: removeBrTags(values.labels),
            datasets: [
                {
                    label: key,
                    data: data,
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
    }

    const chartObject = drawChart(`_${key}`, data, chartConfig);

    const totalChart = chartObject.config.data.labels.length || 0
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

function languageChart(langaugeData) {
    const data = langaugeData["data"]
    const labels = langaugeData["labels"]
    

    var ctx = document.getElementById('language_graphcard').getContext('2d');
    const languageChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users',
                data: data,
                backgroundColor: COLORS.navyBlue,
                borderWidth: 0,
                borderRadius: 20,
                borderSkipped: false,
                barThickness: 18,
                barPercentage: 0.8
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: 'red',
                        fontSize: 12
                    },
                    grid: {
                        color: COLORS.lightGray,
                        borderDash: [2],
                        drawBorder: false,
                        borderWidth: 0,
                        borderDash: [],
                        borderDashOffset: 0,
                        drawTicks: true,
                        display: false
                    },
                    autoSkip: false,
                    maxTicksLimit: 5
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: COLORS.navyBlue,
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }
    drawChart('language_graphcard', data, languageChartConfig)
}

function originChart(originChartData) {
    const data = originChartData["data"]
    const labels = originChartData["labels"]
    
    const originChartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Responses',
                data: data,
                backgroundColor: COLORS.skyBlue,
                borderWidth: 0,
                borderRadius: 20,
                borderSkipped: false,
                barThickness: 18,
                barPercentage: 0.8
            }]
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: 'red',
                        fontSize: 12
                    },
                    grid: {
                        color: COLORS.lightGray,
                        borderDash: [2],
                        drawBorder: false,
                        borderWidth: 0,
                        borderDash: [],
                        borderDashOffset: 0,
                        drawTicks: true,
                        display: false
                    },
                    autoSkip: false,
                    maxTicksLimit: 5
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        display: true,
                        fontColor: COLORS.navyBlue,
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }
    drawChart('destination_graphcard', data, originChartConfig)
}

function destinationChart(destinationData) {


    const data = destinationData["data"]
    const labels = destinationData["labels"]
    var tableHead = $('#origin-table thead');
    tableHead.empty()

    var headerRow = $('<tr></tr>');
    headerRow.append($('<th></th>').text('Origin'));
    headerRow.append($('<th></th>').text('Responses'));
    tableHead.append(headerRow);

    var tableBody = $('#origin-table tbody');
    tableBody.empty()

    if (data.length === 0) {
        const tableRow = $('<tr></tr>');
        tableRow.append($('<td></td>').text('No data available').attr('colspan', '2').css('text-align', 'center'));
        tableBody.append(tableRow);
    } else {
        $.each(labels, function (index, label) {
            var tableRow = $('<tr></tr>');
            tableRow.append($(`<td><div class="py-2 d-flex justify-contents-center" style="color: ${COLORS.navyBlue}">${label}</div></td>`));
            tableRow.append($(`<td><div class="py-2 d-flex justify-contents-center" style="color: ${COLORS.navyBlue}">${data[index]}</div></td>`));
            tableBody.append(tableRow);
        });
    }
}

export_button.addEventListener('click', () => exportToExcel(export_url));
export_button_1.addEventListener('click', () => exportToExcel(export_url_1));
window.addEventListener('DOMContentLoaded', getOriginOptions)
window.addEventListener('DOMContentLoaded', getFactoryOptions)
window.addEventListener('DOMContentLoaded', filterData)