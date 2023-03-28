const export_button = document.querySelector('#exportFileBtn')
const export_url = export_button.attributes.getNamedItem("export-url").value
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

function clearCharts() {
    const canvases = document.querySelectorAll("canvas")
    canvases.forEach(element => element.remove());
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
    document.getElementById('time_range').value = '';
    filterData()
}

function debounce(cb, delay) {
    let timer;
    return function () {
        let context = this;
        clearTimeout(timer);
        timer = setTimeout(() => {
            cb.apply(context, arguments);
        }, delay);
    };
};

function filterData() {
    const url = filter_form.attributes.getNamedItem("submit-url").value;
    const formData = new FormData(filter_form);
    let chartData = {};
    toggleElementDisplay(false, '#chart-area')
    toggleElementDisplay(false, '#no-results')
    toggleElementDisplay(true, '#loader')
    clearFormErrors()
    fetch(url, { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if ('form_errors' in data) {
                setFormErrors(data.form_errors)
            }
            else {
                if (Object.keys(data).length === 0) {
                    toggleElementDisplay(true, '#no-results')
                } else {
                    plotCharts(data)
                    toggleElementDisplay(true, '#chart-area')
                }
            }
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

function plotCharts(chartData) {
    let chartDataKeys = Object.keys(chartData)
    chartDataKeys.map(chartDataKeys => {
        if (chartDataKeys === "age") {
            ageGraph(chartData['age'])
        }

        if (chartDataKeys === "gender") {
            genderGraph(chartData['gender'])
        }

        if (chartDataKeys === "organisation") {
            organisationGraph(chartData['organisation'])
        }
    })
}

function ageGraph(ageGraphData) {
    var ctx = document.getElementById('age-graph').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ageGraphData["labels"],
            datasets: [{
                label: 'Number of Users',
                data: ageGraphData["data"],
                backgroundColor: '#37C1E3',
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
                        color: 'rgba(0, 0, 0, 0.1)',
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
                        fontColor: '#193560',
                        fontSize: 12
                    },
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function genderGraph(genderGraphData) {
    const labels = genderGraphData["labels"]
    const data = genderGraphData["data"]
    const chartData = {
        labels: [
            'Men',
            'Women',
            "Others",
        ],
        datasets: [{
            label: 'My First Dataset',
            data: [70,45, 100],
            backgroundColor: [COLORS.appleGreen,COLORS.skyBlue,COLORS.navyBlue,
            ]
        }]
    };
    const config = {
        type: 'polarArea',
        data: chartData,
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    };

    var ctx = document.getElementById('_gender').getContext('2d');
    new Chart(ctx, config)
}


function organisationGraph(organisationGraphData) {
    const data = organisationGraphData["data"]
    const labels = organisationGraphData["labels"]
    
    var ctx = document.getElementById('_organisation').getContext('2d');

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users',
                data: data,
                backgroundColor: COLORS.appleGreen,
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
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function usersNewUsersChart(){
    var ctx = document.getElementById('users-new-users-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [{
                label: 'USERS',
                data: [12, 19, 3, 5, 2, 3, 7],
                borderColor: COLORS.lightBlue
            }, {
                label: 'NEW USERS',
                data: [6, 9, 12, 5, 8, 7, 10],
                borderColor: COLORS.lightGreen
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                },
            }
        }
    });
}
usersNewUsersChart()

export_button.addEventListener('click', () => exportToExcel(export_url));
end_date.addEventListener('change', debounce(autosubmit, 1000));
start_date.addEventListener('change', debounce(autosubmit, 1000));
window.addEventListener('DOMContentLoaded', getOriginOptions)
window.addEventListener('DOMContentLoaded', getFactoryOptions)
window.addEventListener('DOMContentLoaded', filterData)