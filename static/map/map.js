
function initiateRoutesMap(routes){
    
    var map = L.map('mapid').setView([28.254249510296628, 84.00182396773297], 0);
    map.flyTo([27.98545295039861, 53.278905995774146], 3);
    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        language: 'en',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    for (var i = 0; i < routes.length; i++) {
        var route = routes[i];
    
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

        L.marker([route.from_coords[0], route.from_coords[1]], {
            icon: fromIcon,
            title: route
        }).addTo(map);

        L.marker([route.to_coords[0], route.to_coords[1]], {
            icon: toIcon,
            title: route
        }).addTo(map);
    
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
    }
}
