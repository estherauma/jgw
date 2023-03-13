var map = L.map('mapid').setView([-0.023559, 37.906193], 2);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// mapping through routes
for (var i = 0; i < routes.length; i++) {
    var route = routes[i];

    // marker icon configs
    var fromIcon = L.divIcon({
        className: 'my-icon',
        html: route.from,
        iconSize: [80, 20],
        iconAnchor: [40, 10]
    });
    var toIcon = L.divIcon({
        className: 'my-icon',
        html: route.to,
        iconSize: [80, 20],
        iconAnchor: [40, 10]
    });
    var fromMarker = L.marker([route.from_coords[0], route.from_coords[1]], {
        icon: fromIcon,
        title: route
    }).addTo(map);

    var toMarker = L.marker([route.to_coords[0], route.to_coords[1]], {
        icon: toIcon,
        title: route
    }).addTo(map);
    // marker icon configs ends here


    var color = randomColor();
    var polyline = L.polyline([route.from_coords, route.to_coords], { 
        color: "red", 
        weight: 2
    }).addTo(map);
    polyline.arrowheads({
        frequency: 3,
        fill: true,
        size: '8px',
        color: "#000",

    });
    

    // fit map to show all markers and polylines
    var bounds = new L.LatLngBounds();
    bounds.extend(fromMarker.getLatLng());
    bounds.extend(toMarker.getLatLng());
    bounds.extend(polyline.getBounds());
    map.fitBounds(bounds);
}

// utils
// generate a random color for polyline
function randomColor() {
    return `hsl(${Math.floor(Math.random() * 360)}, 100%, 70%)`;
}
