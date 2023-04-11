function getCountryLatLng(country) {
  switch (country) {
    case "Kazakhstan":
      return [48.0196, 66.9237];
    case "Uzbekistan":
      return [41.3775, 64.5853];
    case "Kyrgyzstan":
      return [41.2044, 74.7661];
    case "Tajikistan":
      return [38.8610, 71.2761];
    case "Ukraine":
      return [48.3794, 31.1656];
    case "India":
      return [20.5937, 78.9629];
    case "Britain (Uk)":
      return [54.7023545, -3.2765751];
    case "South Africa":
      return [-30.5595, 22.9375];
    case "Nepal":
      return [28.3949, 84.1240];
    case "Pakistan":
      return [30.3753, 69.3451];
    case "Russia":
      return [61.5240, 105.3188];
    case "Azerbaijan":
      return [40.1431, 47.5769];
    case "Uganda":
      return [1.3733, 32.2903];
    case "Georgia":
      return [42.3154, 43.3569];
    case "Poland":
      return [51.919438, 19.145136];
    case "Belarus":
      return [53.7098, 27.9534];
    case "Romania":
      return [45.9432, 24.9668];
    case "Moldova":
      return [47.4116, 28.3699];
    case "Albania":
      return [41.1533, 20.1683];
    case "Malaysia":
      return [4.210484, 101.975766];
    case "Bangladesh":
      return [23.6848, 90.3563];
    case "Thailand":
      return [15.8700, 100.9925];
    case "Vietnam":
      return [14.0583, 108.2772];
    case "Serbia":
      return [44.0165, 21.0059];
    case "Bulgaria":
      return [42.7339, 25.4858];
    case "Kenya":
      return [-0.0236, 37.9062];
    case "Saudi Arabia":
      return [23.885942, 45.079162];
    case "United Arab Emirates":
      return [23.424076, 53.847818];
    case "Qatar":
      return [25.354826, 51.183884];
    default:
      return [null, null];
  }
}


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