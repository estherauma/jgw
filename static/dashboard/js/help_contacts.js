const end_date = document.querySelector("#end_date");
const factoryFarm_input = document.querySelector("#factory_farm");
const filter_form = document.querySelector("#filter_form");
const origin_input = document.querySelector("#origin");
const start_date = document.querySelector("#start_date");
const exportHelpContactsBtn = document.querySelector(
  "#export-help-contacts-btn"
);
const exportHelpContactsUrl =
  exportHelpContactsBtn.attributes.getNamedItem("export-url").value;

function toggleElementDisplay(flag, selector) {
  const element = document.querySelector(selector);
  if (flag === true) {
    element.style.display = "block";
  } else if (flag === false) {
    element.style.display = "none";
  }
}

function setFormErrors(errorObject) {
  for (const [key, value] of Object.entries(errorObject)) {
    const element = document.querySelector(`#${key}-errors`);
    element.textContent = value[0];
  }
}

function clearFormErrors() {
  const errorMessages = document.querySelectorAll('[id$="-errors"]');
  for (i in errorMessages) {
    i.textContent = "";
  }
}

function getOriginOptions() {
  const destination_input = document.querySelector("#destination");
  const url = filter_form.attributes.getNamedItem("data-origins-url").value;
  const dest_country = destination_input.value;
  const origin_country = origin_input.value;
  if (dest_country) {
    const filters = new URLSearchParams({ destination: dest_country });
    fetch(`${url}?${filters}`, { method: "GET" })
      .then((response) => {
        result = response.json();
        status_code = response.status;
        if (status_code != 200) {
          console.log("Error processing next field options");
          return false;
        }
        return result;
      })
      .then((data) => {
        options = ``;
        Object.entries(data).map(function ([k, v]) {
          if (k === origin_country) {
            options += `<option value="${k}" selected>${v}</option>`;
          }
          options += `<option value="${k}">${v}</option>`;
        });
        origin_input.innerHTML = options;
        filterData();
      })
      .catch((error) => {
        console.log(error);
      });
  }
}

function getFactoryOptions() {
  const url = filter_form.attributes.getNamedItem("data-factories-url").value;
  const destination_input = document.querySelector("#destination");
  const schemeName_input = document.querySelector("#scheme_name");
  const schemeName = schemeName_input.value;
  const factoryFarm = factoryFarm_input.value;
  const dest_country = destination_input.value;
  const origin_country = origin_input.value;

  if (dest_country && origin_country && schemeName && !factoryFarm) {
    const filters = new URLSearchParams({
      destination: dest_country,
      origin: origin_country,
      scheme_name: schemeName,
    });
    fetch(`${url}?${filters}`, { method: "GET" })
      .then((response) => {
        result = response.json();
        status_code = response.status;
        if (status_code != 200) {
          console.log("Error processing next field options");
          return false;
        }
        return result;
      })
      .then((data) => {
        options = ``;
        Object.entries(data).map(function ([k, v]) {
          if (k === factoryFarm) {
            options += `<option value="${k}" selected>${v}</option>`;
          }
          options += `<option value="${k}">${v}</option>`;
        });
        factoryFarm_input.innerHTML = options;
        filterData();
      })
      .catch((error) => {
        console.log(error);
      });
  }
}

function filterData() {
  const url = filter_form.attributes.getNamedItem("submit-url").value;
  const formData = new FormData(filter_form);
  let chartData = {};
  toggleElementDisplay(false, "#chart-area");
  toggleElementDisplay(true, "#loader");
  toggleElementDisplay(false, "#no-results");
  clearFormErrors();
  fetch(url, { method: "POST", body: formData })
    .then((response) => response.json())
    .then((data) => {
      if ("form_errors" in data) {
        setFormErrors(data.form_errors);
      } else {
        chartData = data["chart_data"];

        if (Object.keys(chartData).length === 0) {
          toggleElementDisplay(true, "#no-results");
        } else {
          plotCharts(chartData);
          toggleElementDisplay(true, "#chart-area");
        }
      }

      const filterStateData = data["filter_state"];
      buildFilterStateAlert("help-contacts", filterStateData);
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => toggleElementDisplay(false, "#loader"));
}

function plotCharts(chartData) {
  if (
    checkObjectProperty(chartData, "phone_number_clicks_by_route") &&
    checkObjectProperty(chartData, "email_clicks_by_route")
  ) {
    const labels = chartData["phone_number_clicks_by_route"]["labels"] || chartData["email_clicks_by_route"]["labels"];
    emailAndPhonenumberClicksByRouteChart(
      chartData["email_clicks_by_route"],
      chartData["phone_number_clicks_by_route"],
      labels
    );
  }
}

function emailAndPhonenumberClicksByRouteChart(
  emailClicks,
  phonenumberClicks,
  labels
) {
  const emailClicksData = emailClicks["data"];
  const phonenumberClicksData = phonenumberClicks["data"];

  const config = {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Email Clicks",
          data: emailClicksData,
          backgroundColor: COLORS.appleGreen,
          borderWidth: 0,
          borderRadius: 20,
          borderSkipped: false,
          barThickness: 18,
          barPercentage: 0.8
        },
        {
          label: "Phonenumber Clicks",
          data: phonenumberClicksData,
        },
      ],
    },
    options: {
      plugins: {},
      responsive: true,
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
        },
      },
    },
  };

  drawChart(
    "email_and_phonenumber_clicks_by_route",
    [...emailClicksData, ...phonenumberClicksData],
    config
  );
}

function exportToExcel(url) {
  const formData = new FormData(filter_form);
  toggleElementDisplay(false, "#chart-area");
  toggleElementDisplay(false, "#no-results");
  toggleElementDisplay(true, "#loader");
  fetch(url, { method: "POST", body: formData })
    .then((response) => {
      if (!response.ok) {
        throw Error(response.statusText);
      } else {
        const header = response.headers.get("Content-Disposition");
        const parts = header.split(";");
        filename = parts[1].split("=")[1].replaceAll('"', "");
        return response.blob();
      }
    })
    .then((blob) => {
      if (blob != null) {
        const a = document.createElement("a");
        a.href = window.URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      toggleElementDisplay(true, "#chart-area");
      toggleElementDisplay(false, "#loader");
    });
}

exportHelpContactsBtn.addEventListener("click", () =>
  exportToExcel(exportHelpContactsUrl)
);
window.addEventListener("DOMContentLoaded", getOriginOptions);
window.addEventListener("DOMContentLoaded", getFactoryOptions);
window.addEventListener("DOMContentLoaded", filterData);
