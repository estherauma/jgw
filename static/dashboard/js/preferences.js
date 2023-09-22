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
                chartData = data['chart_data']
                const user_locations = data['user_locations']
                var map = L.map('users-map').setView([27.98545295039861, 53.278905995774146], 2);

                if(user_locations?.length){
                    userLocationsMap(map, user_locations)
                }

                if (Object.keys(chartData).length === 0) {
                    toggleElementDisplay(true, '#no-results')
                } else {
                    responseCountValue = data['response_count']
                    const responseCountElement = document.querySelector('#response-count')
                    responseCountElement.textContent = responseCountValue
                    plotCharts(chartData)
                    toggleElementDisplay(true, '#chart-area')
                    map.invalidateSize()
                }
            }
            
            const filterStateData = data["filter_state"]
            buildFilterStateAlert('preferences', filterStateData)
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
    clearCharts()
    chartData.preference_user_trends = {
        'new_users': chartData["preference_new_users"],
        'returning_users': chartData["preference_returning_users"],
        'count': chartData["preference_new_and_returning_users"]
    }

    let chartDataKeys = Object.keys(chartData)
    chartDataKeys.map(chartDataKey => {
        if (chartDataKey === "preference_age") {
            ageGraph(chartData['preference_age'])
        }

        if (chartDataKey === "preference_gender") {
            genderGraph(chartData['preference_gender'])
        }

        if (chartDataKey === "preference_organisation") {
            organisationGraph(chartData['preference_organisation'])
        }

        if (chartDataKey === "preference_language") {
            preferenceLanguageChart(chartData['preference_language'])
        }

        if (chartDataKey === "preference_origin") {
            preferenceOriginChart(chartData['preference_origin'])
        }

        if (chartDataKey === "preference_destination") {
            preferenceDestinationChart(chartData['preference_destination'])
        }
        if (chartDataKey === "preference_user_trends" ) {
            userTrendsGraph(chartData['preference_user_trends'])
        }
    })
}

function ageGraph(ageGraphData) {
    const data = ageGraphData["data"];
    const chartConfig =  {
        type: 'bar',
        data: {
            labels: ageGraphData["labels"],
            datasets: [{
                label: 'NUMBER OF USERS',
                data: data,
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
    }
    drawChart('age-graph', data, chartConfig);
}

function genderGraph(genderGraphData) {
    const labels = genderGraphData["labels"]
    const data = genderGraphData["data"]
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'User',
            data: data,
            backgroundColor: [COLORS.darkBlue, COLORS.appleGreen,COLORS.skyBlue,COLORS.navyBlue, COLORS.black]
        }]
    };
    const config = {
        type: 'pie',
        data: chartData,
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    };

    drawChart('_gender', data, config);
}


function organisationGraph(organisationGraphData) {
    const data = organisationGraphData["data"]
    const labels = organisationGraphData["labels"]

    const chartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'NUMBER OF USERS',
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
                    title: {
                        display: true,
                        text: 'NUMBER OF USERS'
                    },
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
                },
                datalabels: {
                    anchor: 'end',
                    align: 'end',
                    formatter: (value)  => changeThousandsToLetterK(value)
                }
            },
            layout: {
                padding: {
                    bottom: 20
                }
            }
        },
        plugins: [ChartDataLabels]
    }

    drawChart('_organisation', data, chartConfig);
}

function userTrendsGraph(trendsData) {
    const ctx = document.getElementById('preference_user_trends').getContext("2d");
    const new_users = trendsData.new_users
    const returning_users = trendsData.returning_users
    const count = trendsData.count
    const new_users_count = count.data[0]
    const returning_users_count = count.data[1]

    firstGraphBg = COLORS.navyBlue;
    secondGraphOneBg = COLORS.skyBlue;

    const chartConfig = {
      type: "line",
      data: {
        labels: new_users.labels,
        datasets: [
          {
            ...genericBarGraphDatasetConfig,
            label: 'New users',
            data: new_users.data,
            backgroundColor: firstGraphBg,
            borderColor:firstGraphBg
          },
          {
            ...genericBarGraphDatasetConfig,
            label: 'Users',
            data: returning_users.data,
            backgroundColor: secondGraphOneBg,
            borderColor:secondGraphOneBg
          },
        ],
      },
      options: {
        scales: {
          x: {
            ticks: {
              autoSkip: false, 
                maxRotation: 0,
                callback: function (value, index, values) {
                  // Show the label only for every 6th date
                  if (index % 6 === 0) {
                    return new_users.labels[index];
                   } else {
                      return ''; //index,  Return an empty string for other labels
                   }
                },        
            },
            grid: {
              display: false,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              display: true,
            },
          },
        },
        plugins: {
          legend: {
            display: true,
            position: 'right',
            align: 'start', 
          },
        },
      },
    };

    const captionElement = document.getElementById('preference_user_trends_caption');
    const startDate = convertDateToLongFormat(new_users.labels[0]);
    const endDate = convertDateToLongFormat(new_users.labels[new_users.labels.length - 1])
    const dateRangeText = `Between ${startDate} - ${endDate} there was a total of  <strong>${returning_users_count}</strong> users and <strong>${new_users_count}</strong> new users`;
    captionElement.innerHTML = dateRangeText;
   
    new Chart(ctx, chartConfig);
}

function userLocationsMap(map,data){
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        language: 'en',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    for (let i = 0; i < data.length; i++) {
        const location = data[i];

        if(location.coords.length<1){
            continue;
        }
        var marker = L.marker(location.coords).addTo(map);

        var tooltipContent = '<b>' + location.country + '</b><br>Users: ' + location.users;
        marker.bindTooltip(tooltipContent);
        createLocationsTable(location)
    }
}

function createLocationsTable(data){
    var table = document.getElementById('location-table-body');
    var row = document.createElement("tr");
    var countryCell= document.createElement("td");
    var usersCell  = document.createElement("td");

    countryCell.textContent = toTitleCase(data.country)
    countryCell.style.backgroundColor = COLORS.navyBlue; 

    usersCell.textContent = data.users
    usersCell.style.backgroundColor = COLORS.skyBlue; 

    row.appendChild(countryCell);
    row.appendChild(usersCell);
    table.appendChild(row);
}


export_button.addEventListener('click', () => exportToExcel(export_url));
window.addEventListener('DOMContentLoaded', getOriginOptions)
window.addEventListener('DOMContentLoaded', getFactoryOptions)
window.addEventListener('DOMContentLoaded', filterData)