function createUserOriginMap(data, elementId ) {
    const countryUserCounts = {};
    const OFFSET = 0.02;

    data.forEach(row => {
        const { origin, count } = row;

        if (origin) {
            countryUserCounts[origin] = (countryUserCounts[origin] || 0) + count;
        }
    });

    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        locations: Object.keys(countryUserCounts),
         z: Object.values(countryUserCounts).map(count => count / 1000),
        // z: Object.values(countryUserCounts),
        text: Object.keys(countryUserCounts).map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        colorscale: [
            [0, '#e3d7ff'], 
            [0.5, '#b39ddb'],
            [1, '#673ab7']
        ],
        reversescale: false,
        colorbar: {
            // title: 'Users (Thousands)',
            title: 'Users',
            // tickprefix: '',
            // ticksuffix: 'k',
            thickness: 10
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
            // lataxis: { range: [-60, 95] },
        },
        margin: { t: 0, b: 0, l: 0, r: 0 },
        width: containerWidth,
        height: containerHeight
    };

    Plotly.newPlot(elementId, allTraces, layout, {
        responsive: true,
        scrollZoom: true,
        displayModeBar: false,
    });

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
// Function to create a map of'text' user destinations

function createUserDestinationMap(data, elementId, countryCoords ) {
    const countryUserCounts = {};
    const OFFSET = 0.02;

    data.forEach(row => {
        const { destination, count } = row;

        if (countryCoords[destination]) {
            countryUserCounts[destination] = (countryUserCounts[destination] || 0) + count;
        }
    });

    const choroplethTrace = {
        type: 'choropleth',
        locationmode: 'country names',
        locations: Object.keys(countryUserCounts),
        z: Object.values(countryUserCounts).map(count => count / 1000),
        // z: Object.values(countryUserCounts),
        text: Object.keys(countryUserCounts).map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        colorscale: [
            [0, '#e3d7ff'], 
            [0.5, '#b39ddb'],
            [1, '#673ab7']
        ],
        reversescale: false,
        colorbar: {
            // title: 'Users (Thousands)',
            title: 'Users',
            // tickprefix: '',
            // ticksuffix: 'k',
            thickness: 10
        },
        hoverinfo: 'text'
    };

    const markerTrace = {
        type: 'scattergeo',
        locationmode: 'country names',
        text: Object.keys(countryUserCounts).map(
            country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
        ),
        mode: 'markers',
        marker: {
            size: 6,
            color: '#673ab7',
            line: {
                color: 'white',
                width: 1
            }
        },
        lat: Object.keys(countryUserCounts).map(
            country => countryCoords[country]?.lat || null
        ).filter(lat => lat !== null), // Filter out undefined coordinates
        lon: Object.keys(countryUserCounts).map(
            country => countryCoords[country]?.lon || null
        ).filter(lon => lon !== null), // Filter out undefined coordinates
        hoverinfo: 'text'
    };

    const allTraces = [choroplethTrace, markerTrace];

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
            // lataxis: { range: [-60, 95] },
        },
        margin: { t: 0, b: 0, l: 0, r: 0 },
        width: containerWidth,
        height: containerHeight
    };

    Plotly.newPlot(elementId, allTraces, layout, {
        responsive: true,
        scrollZoom: true,
        displayModeBar: false,
    });

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
// function createUserDestinationMap(data, elementId) {
//     const countryUserCounts = {};

//     data.forEach(row => {
//         const { destination, count } = row;

//         if (destination) {
//             countryUserCounts[destination] = (countryUserCounts[destination] || 0) + count;
//         }
//     });

//     const maxCount = Math.max(...Object.values(countryUserCounts));

//     const choroplethTrace = {
//         type: 'choropleth',
//         locationmode: 'country names',
//         locations: Object.keys(countryUserCounts),
//         z: Object.values(countryUserCounts).map(count => Math.max(count, 1)), // Ensure all countries have a value
//         text: Object.keys(countryUserCounts).map(
//             country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
//         ),
//         colorscale: [
//             [0, '#e3d7ff'],  // Very light violet (low intensity)
//             [0.1, '#c7b4f7'],
//             [0.3, '#b39ddb'], 
//             [0.5, '#9575cd'], 
//             [0.8, '#7e57c2'], 
//             [1, '#673ab7']    // Dark violet (high intensity)
//         ],
//         zmin: 1,  // Minimum value (at least 1 user)
//         zmax: maxCount,  // Maximum value
//         reversescale: false,
//         colorbar: {
//             title: 'Users',
//             thickness: 10
//         },
//         hoverinfo: 'location+text'
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
//             }
//         },
//         margin: { t: 0, b: 0, l: 0, r: 0 },
//         width: containerWidth,
//         height: containerHeight
//     };

//     Plotly.newPlot(elementId, allTraces, layout, {
//         responsive: true,
//         scrollZoom: false,
//         displayModeBar: false,
//     });

//     window.addEventListener('resize', () => {
//         Plotly.Plots.resize(elementId);
//     });
// }

// function capitalizeFirstLetter(string) {
//     return string.charAt(0).toUpperCase() + string.slice(1);
// }


// function createUserDestinationMap(data, elementId ) {
//     const countryUserCounts = {};

//     data.forEach(row => {
//         const { destination, count } = row;

//         if (destination) {
//             countryUserCounts[destination] = (countryUserCounts[destination] || 0) + count;
//         }
//     });

//     const choroplethTrace = {
//         type: 'choropleth',
//         locationmode: 'country names',
//         locations: Object.keys(countryUserCounts),
//         z: Object.values(countryUserCounts),
//         // z: Object.values(countryUserCounts).map(count => count / 1000),
//         text: Object.keys(countryUserCounts).map(
//             country => `${capitalizeFirstLetter(country)}: ${countryUserCounts[country]} Users`
//         ),
//         colorscale: [
//             [0, '#e3d7ff'], // Very light violet (low intensity)
//             [0.5, '#b39ddb'], // Medium violet
//             [1, '#673ab7']    // Dark violet (high intensity)
//         ],
//         reversescale: false,
//         colorbar: {
//             title: 'Users',
//             thickness: 10
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
//             }
//         },
//         margin: { t: 0, b: 0, l: 0, r: 0 },
//         width: containerWidth,
//         height: containerHeight
//     };

//     Plotly.newPlot(elementId, allTraces, layout, {
//         responsive: true,
//         scrollZoom: false,
//         displayModeBar: false,
//     });

//     window.addEventListener('resize', () => {
//         Plotly.Plots.resize(elementId);
//     });
// }

// function capitalizeFirstLetter(string) {
//     return string.charAt(0).toUpperCase() + string.slice(1);
// }
