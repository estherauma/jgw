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
        text: Object.keys(countryUserCounts).map(
            country => `${country}: ${countryUserCounts[country]} Users`
        ),
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

    Plotly.newPlot(elementId, [choroplethTrace], layout, config);

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}
