function createUserRouteMap(data, elementId, countryCoords) {
    const traces = data.map(row => {
        const origin = row.origin;
        const destination = row.destination;

        if (countryCoords[origin] && countryCoords[destination]) {
            const hoverText = data
                .filter(row => row.origin === origin)
                .map(row => `${capitalizeFirstLetter(row.destination)}: ${row.count}`)
                .join('<br>');
            
            return {
                type: 'scattergeo',
                lon: [countryCoords[origin][1], countryCoords[destination][1]],
                lat: [countryCoords[origin][0], countryCoords[destination][0]],
                mode: 'lines+markers',
                line: {
                    width: 2,
                    color: '#193560'
                },
                opacity: 0.3,
                text: `${capitalizeFirstLetter(origin)}<br>${hoverText}`,
                hoverinfo: 'text',
                marker: {
                    symbol: 'arrow',
                    size: 15,
                    color: '#193560',
                    angle: 45,
                    angleref: 'previous'
                }
            };
        }
        return null;
    }).filter(trace => trace !== null);

    const countries = [...new Set(data.map(row => row.origin).concat(data.map(row => row.destination)))];
    const markerTraces = countries.map(country => {
        if (countryCoords[country]) {
            const totalCount = data.filter(row => row.origin === country || row.destination === country)
                .reduce((sum, row) => sum + row.count, 0);
            return {
                type: 'scattergeo',
                lon: [countryCoords[country][1]],
                lat: [countryCoords[country][0]],
                text: `${capitalizeFirstLetter(country)}: ${totalCount} Users`,
                mode: 'markers+text',
                marker: {
                    size: 16,
                    symbol: 'circle-dot',
                    color: '#37c1e3',
                    line: {
                        width: 2,
                        color: '#193560'
                    }
                },
                textposition: 'right',
                textfont: {
                    family: 'Arial, sans-serif',
                    size: 12,
                    color: 'black'
                },
                name: capitalizeFirstLetter(country),
                hoverinfo: 'text',
                textbackground: {
                    color: 'rgba(255, 255, 255, 0.8)',
                    bordercolor: '#193560',
                    borderwidth: 1,
                    borderpad: 2
                }
            };
        }
        return null;
    }).filter(trace => trace !== null);

    const allTraces = [...traces, ...markerTraces];

    let minLat = Infinity, maxLat = -Infinity, minLon = Infinity, maxLon = -Infinity;
    countries.forEach(country => {
        if (countryCoords[country]) {
            const [lat, lon] = countryCoords[country];
            minLat = Math.min(minLat, lat);
            maxLat = Math.max(maxLat, lat);
            minLon = Math.min(minLon, lon);
            maxLon = Math.max(maxLon, lon);
        }
    });

    const container = document.getElementById(elementId);
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    const layout = {
        title: 'User Route Map',
        showlegend: false,
        geo: {
            showland: true,
            showcountries: true,
            showocean: true,
            countrywidth: 0.5,
            landcolor: 'rgb(243, 243, 243)',
            lakecolor: 'rgb(255, 255, 255)',
            oceancolor: 'rgb(230, 255, 255)',
            projection: {
                type: 'mercator'
            },
            lonaxis: {
                range: [minLon - 15, maxLon + 10]
            },
            lataxis: {
                range: [minLat - 15, maxLat + 10]
            }
        },
        width: containerWidth,
        height: containerHeight,
        margin: { t: 0, b: 0, l: 0, r: 0 },  
        dragmode: true  
    };

    const initialRange = {
        lon: layout.geo.lonaxis.range,
        lat: layout.geo.lataxis.range
    };

    Plotly.newPlot(elementId, allTraces, layout, {
        responsive: true,
        scrollZoom: false,
        modeBarButtonsToRemove: ['pan2d'],
        displayModeBar: true,
    }).then(function(gd) {
        gd.on('plotly_relayout', function(eventData) {
            const newRange = {
                lon: eventData['geo.lonaxis.range'] || initialRange.lon,
                lat: eventData['geo.lataxis.range'] || initialRange.lat
            };

            const initialWidth = initialRange.lon[1] - initialRange.lon[0];
            const initialHeight = initialRange.lat[1] - initialRange.lat[0];
            const newWidth = newRange.lon[1] - newRange.lon[0];
            const newHeight = newRange.lat[1] - newRange.lat[0];

            if (newWidth > initialWidth * 1.1 || newHeight > initialHeight * 1.1) {
                Plotly.relayout(elementId, {
                    'geo.lonaxis.range': initialRange.lon,
                    'geo.lataxis.range': initialRange.lat
                });
            }
        });
    });

    function animateLines() {
        const visibleDuration = 4000; 
        const hiddenDuration = 2000; 

        function toggleLines() {
            Plotly.restyle(elementId, {
                visible: true
            }, traces.map((_, i) => i));

            setTimeout(() => {
                Plotly.restyle(elementId, {
                    visible: false
                }, traces.map((_, i) => i));

                setTimeout(toggleLines, hiddenDuration);
            }, visibleDuration);
        }

        toggleLines();
    }

    animateLines();

    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elementId);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
