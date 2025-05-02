function createUserGeolocationMap(data, elementId) {
    const countryUserCounts = {};

    data.forEach(row => {
        const { country, count } = row;
        if (country) {
            countryUserCounts[country] = (countryUserCounts[country] || 0) + count;
        }
    });

    const countries = Object.keys(countryUserCounts).filter(country => country !== "Antarctica");
    const container = document.getElementById(elementId);
    const containerWidth = container ? container.offsetWidth || "100%" : "100%";
    const containerHeight = container ? container.offsetHeight || 800 : 800;

    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        locations: countries,
        z: Object.values(countryUserCounts),
        text: countries.map(country => `${country}: ${countryUserCounts[country]} Users`),
        colorscale: [
            [0, '#E8F9D5'], 
            [0.5, '#B7DC6E'], 
            [1, '#9BC917']
        ],
        reversescale: false,
        colorbar: {
            title: 'Users',
            thickness: 10,
            x: elementId === 'user_geolocation_map' ? 0.92 : 1.05,
            xpad: 50
        },
        hoverinfo: 'text'
    };

    const layout = {
        geo: {
            showland: true,
            showcountries: true,
            countrywidth: 0.2,
            landcolor: 'rgb(240, 240, 240)',
            oceancolor: 'rgb(230, 255, 255)',
            showocean: true,
            projection: { type: 'mercator' },
            lataxis: { range: [-60, 90] },
            lonaxis: { range: [-180, 180] }
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
            'pan2d', 'toImage', 'select2d', 'lasso2d', 'hoverClosestGeo',
            'hoverClosestCartesian', 'hoverCompareCartesian', 'autoScale2d',
            'resetScale2d', 'toggleHover', 'resetViews'
        ],
        modeBarButtonsToAdd: ['zoomInGeo', 'zoomOutGeo', 'resetGeo'],
        displaylogo: false
    };

    Plotly.newPlot(elementId, [choroplethTrace], layout, config).then(() => {
        updateModebarPosition(elementId);
    });

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
        updateModebarPosition(elementId);
    });
}

function updateModebarPosition(elementId) {
    const container = document.getElementById(elementId);
    const modeBar = container?.querySelector('.modebar');
    if (!container || !modeBar) return;

    const width = container.offsetWidth;

    modeBar.classList.add(`${elementId}-modebar`);
    
    if (elementId === 'user_geolocation_map') {
        modeBar.style.right = `${Math.max(width * 0.1, 20)}px`;
        modeBar.style.top = '-5px';
    } else if (elementId === 'user_geolocation_map_user_engagement') {
        modeBar.style.right = `${Math.max(width * 0.07, 10)}px`;
        modeBar.style.top = '5px';
    }
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
