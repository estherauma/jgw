function createUserGeolocationMap(data, elementId) {
   
    const countries = data.map(row => row.country);
    const counts = data.map(row => row.user_count);
    const hoverTexts = data.map(row => `${row.country}: ${row.user_count} Users`);

    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        locations: countries,
        z: counts,
        text: hoverTexts,
        colorscale: [
            [0, '#E8F9D5'],
            [0.5, '#B7DC6E'],
            [1, '#9BC917']
        ],
        reversescale: false,
        colorbar: {
            title: 'Users',
            thickness: 10,
            x: 1.05,
            xpad: 50
        },
        hoverinfo: 'text'
    };

    const allTraces = [choroplethTrace];

    const container = document.getElementById(elementId);
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    const layout = {
        geo: {
            showland: true,
            showcountries: true,
            countrywidth: 0.2,
            landcolor: 'rgb(240, 240, 240)',
            oceancolor: 'rgb(230, 255, 255)',
            showocean: true,
            projection: {
                type: 'mercator'
            },
            lataxis: {
                range: [-60, 90]
            },
            lonaxis: {
                range: [-180, 180]
            }
        },
        margin: { t: 0, b: 0, l: 0, r: 0 },
        width: containerWidth,
        height: containerHeight
    };

    const config = {
        responsive: true,
        scrollZoom: true,
        displayModeBar: true,
        modeBarButtonsToRemove: [
            'pan2d',
            'toImage',
            'select2d',
            'lasso2d',
            'hoverClosestGeo',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'autoScale2d',
            'resetScale2d',
            'toggleHover',
            'resetViews'
        ],
        modeBarButtonsToAdd: [
            'zoomInGeo',
            'zoomOutGeo',
            'resetGeo'
        ],
        displaylogo: false
    };

    Plotly.newPlot(elementId, allTraces, layout, config);

    const modeBar = container.querySelector('.modebar-container');
    if (modeBar) {
        modeBar.style.right = '80px';
        modeBar.style.top = '5px';
    }

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
