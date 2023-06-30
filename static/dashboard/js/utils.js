const idToIgnoreWhenRecreatingRemovedCharts = ['_question']

function clearCharts() {
  const canvases = document.querySelectorAll("canvas");
  canvases.forEach(element => {

    if(idToIgnoreWhenRecreatingRemovedCharts.includes(element.id)) {
      element.remove()
      return;
    }

    const newCanvas = document.createElement("canvas");
    newCanvas.id = element.id; // set the new canvas id to the same value as the old canvas id
    element.parentNode.replaceChild(newCanvas, element);
  });
}

function formDataToObject(formData) {
  const normalizeValues = (values) => (values.length > 1) ? values : values[0];
  const formElemKeys = Array.from(formData.keys());
  const finalKeysArray = formElemKeys.filter(formElemKey => formElemKey !== 'csrfmiddlewaretoken');

  return Object.fromEntries(
    finalKeysArray.map(key => 
      {
        return [key, normalizeValues(formData.getAll(key))]
      })
  );
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


function buildFilterStateAlert(filterStateContainerId, data) {
  const filterStateContainer = document.querySelector(`#${filterStateContainerId}-filter-state-container`)

  const existingSpan = filterStateContainer.querySelector('span');
  if (existingSpan) {
      filterStateContainer.removeChild(existingSpan);
  }

  const span = document.createElement('span');
  let formattedText = '';
  for (const key in data[0]) {
      formattedText += `<strong>${key}:</strong> ${data[0][key]}<br>`;
  }
  span.innerHTML = formattedText;
  filterStateContainer.appendChild(span);
}


function drawChart(canvasId, data, chartConfig, noDataMessage = "No data available") {
  var canvas = document.getElementById(canvasId);
  var ctx = canvas.getContext('2d');
  var sum = data.reduce(function(a, b) { return a + b; }, 0);
  var parent = canvas.parentNode;
  var existingMessage = parent.querySelector('.chart-message');
  
  if (data.length === 0 || sum === 0) {
    if (existingMessage) {
      parent.removeChild(existingMessage);
    }

    canvas.style.display = "none";
    var message = document.createElement('p');
    message.classList.add('chart-message');
    message.textContent = noDataMessage;
    parent.appendChild(message);

    return new Chart(ctx, {});
  } else {
    if (existingMessage) {
      parent.removeChild(existingMessage);
    }

    canvas.style.display = "block";
    return new Chart(ctx, chartConfig);
  }
}

function scrollableVerticalBarChart(containerId, data, chartConfig) {
  graphDiv = document.getElementById(containerId)
  
  let canvas = document.createElement('canvas')
  let canvasId = `canvas_${containerId}`
  canvas.setAttribute('id', canvasId)
  canvas.setAttribute('class', "chartContainer")
  graphDiv.appendChild(canvas)

  const chartObject = drawChart(canvasId, data, chartConfig)

  const totalChart = chartObject.config.data.labels.length
  let totalHeight;

  /** 
      if the number of bars are > 25, add generic-chart-box class to currentChartBox
      to make it scrollable instead of a very long chart
  **/
  let currentChartBox = document.querySelector(`.${containerId}-chart-box`)

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

function checkObjectProperties(obj, properties) {
  for (let i = 0; i < properties.length; i++) {
    if (!obj.hasOwnProperty(properties[i])) {
      return false;
    }
  }
  return true;
}

function checkObjectProperty(obj, property) {
  return obj.hasOwnProperty(property);
}

function changeThousandsToLetterK(value) {
  if(value >  1000) {
    return (value/1000) + "K"
  }
  return value
}

const shuffleArray = array => {
  return Array(array.length).fill(null)
      .map((_, i) => [Math.random(), i])
      .sort(([a], [b]) => a - b)
      .map(([, i]) => array[i])
}

function stopScrollPropagation(event) {
  event.stopPropagation();
}