window.onload = function() {
    var mapLayer = MQ.mapLayer(), map;

    map = L.map('map', {
        layers: mapLayer,
        center: [ 0, 25 ],
        zoom: 12
    });

    var dir = MQ.routing.directions();
    dir.route({
    locations: [
        {latLng: {lat: 1.3733, lng: 32.2903}},
        {latLng: {lat: 23.8859, lng: 45.0792}}
    ]
    });
    map.addLayer(MQ.routing.routeLayer({
        directions: dir,
        fitBounds: true
    }));

}

// {latLng: {lat: 0.3476, lng: 32.5825}},
// {latLng: {lat: 0.3864, lng: 32.6261}}