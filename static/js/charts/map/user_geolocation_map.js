function createUserOriginMap(data, elementId ) {
    const countryUserCounts = {};

    data.forEach(row => {
        const { origin, count } = row;

        if (origin) {
            countryUserCounts[origin] = (countryUserCounts[origin] || 0) + count;
        }
    });

     // Filter out Antarctica from the data
     const countries = Object.keys(countryUserCounts).filter(country => country !== "Antarctica");


    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        // locations: Object.keys(countryUserCounts),
        locations: countries, // Use filtered countries (without Antarctica)
        //  z: Object.values(countryUserCounts).map(count => count / 1000),
        z: Object.values(countryUserCounts),
        text: Object.keys(countryUserCounts).map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        colorscale: [
            [0, '#e0f7e0'], // Light green
            [0.5, '#66bb66'], // Medium green
            [1, '#006400'] // Dark green
        ],
        reversescale: false,
        colorbar: {
            title: 'Users',
            thickness: 10,
            x: 1.05, // Move the color bar slightly to the right
            xpad: 50 // Add left margin by padding

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
                range: [-60, 90] // Restricting the latitude range to avoid Antarctica
            },
            lonaxis: {
                range: [-180, 180] // Keep longitude range as standard
            },
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

    Plotly.newPlot(elementId, allTraces, layout, config );

    const modeBar = container.querySelector('.modebar-container');
    if (modeBar) {
        modeBar.style.right = '90px';
        modeBar.style.top = '5px';
    }

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function createUserDestinationMap(data, elementId) {
    const countryUserCounts = {};

    data.forEach(row => {
        const { destination, count } = row;

        if (destination) {
            countryUserCounts[destination] = (countryUserCounts[destination] || 0) + count;
        }
    });

    // Filter out Antarctica from the data
    const countries = Object.keys(countryUserCounts).filter(country => country !== "Antarctica");

    // Separate countries with low counts for scattergeo
    const lowUserCountries = countries.filter(
        country => countryUserCounts[country] < 100 // Define "low count" threshold
    );

    // Define the choropleth trace for higher-density countries
    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        locations: countries.filter(country => !lowUserCountries.includes(country)), // Exclude low-count countries
        z: countries
            .filter(country => !lowUserCountries.includes(country))
            .map(country => countryUserCounts[country]),
        text: countries.map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        colorscale: [
            [0, '#e0f7e0'], // Light green
            [0.5, '#66bb66'], // Medium green
            [1, '#006400'] // Dark green
        ],
        reversescale: false,
        colorbar: {
            title: 'Users',
            thickness: 10,
            x: 1.05, // Move the color bar slightly to the right
            xpad: 50 // Add left margin by padding
        },
        hoverinfo: 'text'
    };

    // Add scattergeo trace for low-user-count countries
    const scattergeoTrace = {
        type: 'scattergeo',
        locationmode: 'country names',
        locations: lowUserCountries, // Explicitly plot low-count countries
        text: lowUserCountries.map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        marker: {
            size: 6, // Customize marker size
            color: '#006400', // Match the darkest green color
            line: {
                color: '#000',
                width: 1
            }
        },
        hoverinfo: 'text'
    };

    const allTraces = [choroplethTrace, scattergeoTrace];

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
            },
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

// // Destination Map
// function createUserDestinationMap(data, elementId ) {
//     const countryUserCounts = {};

//     data.forEach(row => {
//         const { destination, count } = row;

//         if (destination) {
//             countryUserCounts[destination] = (countryUserCounts[destination] || 0) + count;
//         }
//     });

//      // Filter out Antarctica from the data
//      const countries = Object.keys(countryUserCounts).filter(country => country !== "Antarctica");
    
//     const choroplethTrace = {
//         type: 'choropleth',
//         locationmode: 'country names',
//         // locations: Object.keys(countryUserCounts),
//         locations: countries, // Use filtered countries (without Antarctica)
//         //  z: Object.values(countryUserCounts).map(count => count / 1000),
//         z: Object.values(countryUserCounts),
//         text: Object.keys(countryUserCounts).map(
//             country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
//         ),
//         colorscale: [
//             [0, '#e0f7e0'], // Light green
//             [0.5, '#66bb66'], // Medium green
//             [1, '#006400'] // Dark green
//         ],
//         reversescale: false,
//         colorbar: {
//             title: 'Users',
//             thickness: 10,
//             x: 1.05, // Move the color bar slightly to the right
//             xpad: 50 // Add left margin by padding

//         },
//         hoverinfo: 'text'
//     };

//     const allTraces = [choroplethTrace];

//     const container = document.getElementById(elementId);
//     const containerWidth = container.offsetWidth;
//     const containerHeight = container.offsetHeight;

//     const layout = {
//         geo: {
//             showland: true,
//             showcountries: true,
//             countrywidth: 0.2,
//             landcolor: 'rgb(240, 240, 240)',
//             oceancolor: 'rgb(230, 255, 255)',
//             showocean: true,
//             projection: {
//                 type: 'mercator'
//             },
//             lataxis: {
//                 range: [-60, 90]
//             },
//             lonaxis: {
//                 range: [-180, 180]
//             },
//         },
//         margin: { t: 0, b: 0, l: 0, r: 0 },
//         width: containerWidth,
//         height: containerHeight
//     };

//     const config = {
//         responsive: true,
//         scrollZoom: true,
//         displayModeBar: true,
//         modeBarButtonsToRemove: [
//             'pan2d',
//             'toImage', 
//             'select2d', 
//             'lasso2d', 
//             'hoverClosestGeo', 
//             'hoverClosestCartesian',
//             'hoverCompareCartesian',
//             'autoScale2d',
//             'resetScale2d',
//             'toggleHover',
//             'resetViews'
//         ],
//         modeBarButtonsToAdd: [
//             'zoomInGeo', 
//             'zoomOutGeo', 
//             'resetGeo'
//         ],
//         displaylogo: false 
//     };

//     Plotly.newPlot(elementId, allTraces, layout, config);

//     const modeBar = container.querySelector('.modebar-container');
//     if (modeBar) {
//         modeBar.style.right = '80px';
//         modeBar.style.top = '5px';
//     }

//     window.addEventListener('resize', () => {
//         Plotly.Plots.resize(elementId);
//     });
// }

// function capitalizeFirstLetter(string) {
//     return string.charAt(0).toUpperCase() + string.slice(1);
// }
