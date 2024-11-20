function createUserRouteMap(data, elementId, countryCoords) {
    const traces = data.map(row => {
        const origin = row.origin;
        const destination = row.destination;
        const OFFSET = 0.02;
     
        if (countryCoords[origin] && countryCoords[destination]) {
            const totalUsersFromOrigin = data
                .filter(d => d.origin === origin)
                .reduce((sum, d) => sum + d.count, 0);
    
            const totalUsersToDestination = data
                .filter(d => d.destination === destination)
                .reduce((sum, d) => sum + d.count, 0);
    
            const originData = data.filter(d => d.origin === origin);
            const originHoverText = `From ${capitalizeFirstLetter(origin)}: ${totalUsersFromOrigin} users<br>` +
                (originData.length > 0 ?
                    originData.map(d => `To ${capitalizeFirstLetter(d.destination)}: ${d.count} users`).join('<br>') :
                    'No users traveled');
    
            const destinationData = data.filter(d => d.destination === destination);
            const destinationHoverText = `To ${capitalizeFirstLetter(destination)}: ${totalUsersToDestination} users<br>` +
                (destinationData.length > 0 ?
                    destinationData.map(d => `From ${capitalizeFirstLetter(d.origin)}: ${d.count} users`).join('<br>') :
                    'No users came in');

            return [                
                {
                    type: 'scattergeo',
                    lon: [countryCoords[origin][1], countryCoords[destination][1]+ OFFSET],
                    lat: [countryCoords[origin][0], countryCoords[destination][0]+ OFFSET],
                    text: destinationHoverText,
                    mode: 'markers+lines',
                    hoverinfo: 'text',
                    line: {
                        width: 2,
                        color: '#193560',
                        dash: 'dash'
                    },
                    opacity: 0.4, 
                    showlegend: false 
                },
                {
                    type: 'scattergeo',
                    lon: [countryCoords[origin][1]],
                    lat: [countryCoords[origin][0]],
                    text: originHoverText,
                    mode: 'markers',
                    hoverinfo: 'text',
                    marker: {
                        size: 8,
                        color: '#37c1e3'
                    },
                    showlegend: false 
                }
            ];
    
        }
        return null;
    }).flat().filter(trace => trace !== null);

    const countries = [...new Set(data.map(row => row.origin).concat(data.map(row => row.destination)))];
    
    const legendGroupsAdded = new Set();
    const markerTraces = countries.map(country => {
        if (countryCoords[country]) {
            const totalCount = data.filter(row => row.origin === country || row.destination === country)
                .reduce((sum, row) => sum + row.count, 0);
        
            const isOrigin = data.some(d => d.origin === country);
            const isDestination = data.some(d => d.destination === country);
    
            let color;
            let legendgroup;
            let name; 
            let showlegend = false; 
    
            if (isOrigin && isDestination) {
                color = '#FFFF00';
                legendgroup = 'both';
                name = 'Both Origin and Destination';
            } else if (isOrigin) {
                color = '#37c1e3';
                legendgroup = 'origin';
                name = 'Origin';
            } else if (isDestination) {
                color = '#00FF00';
                legendgroup = 'destination';
                name = 'Destination';
            }

            if (!legendGroupsAdded.has(legendgroup)) {
                showlegend = true;
                legendGroupsAdded.add(legendgroup); 
            }
        
            return {
                type: 'scattergeo',
                lon: [countryCoords[country][1]],
                lat: [countryCoords[country][0]],
                text: `${capitalizeFirstLetter(country)}: ${totalCount} Users`,
                mode: 'markers',
                marker: {
                    size: 16,
                    symbol: 'circle-dot',
                    color: color,
                    line: {
                        width: 4,
                        color: '#193560',
                    }
                },
                textposition: 'right',
                textfont: {
                    family: 'Arial, sans-serif',
                    size: 12,
                    color: 'black',
                },
                name: showlegend ? name : "", 
                legendgroup: legendgroup, 
                showlegend: showlegend,
                hoverinfo: 'text'
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
        showlegend: true,
        legend: {
            orientation: 'h',
            x: 0.5,
            y: 1.1,
            xanchor: 'center'
        },
        geo: {
            showland: true,
            showcountries: true,
            showocean: true,
            countrywidth: 0.2,
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
        displayModeBar: false,
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
