$(document).ready(function(){
    var map = L.mapbox.map('map', '{{ MAPBOX_MAP_ID }}')
        .setView([38.754, -97.734], 4);

    // Layer to hold our geo objects
    var markersLayer = L.geoJson().addTo(map);
});

function nhdSearch() {
    var lat = document.getElementById('latitude').value;
    var lon = document.getElementById('longitude').value;
    var name = document.getElementById('name').value;

    // Clear any existing geo objects from map
    markersLayer.clearLayers();

    // Clear table of rivers
    $('#river-list tr').not(':first').remove();

    // Add a marker for the searched on lat lon
    markersLayer.addLayer(L.marker([lat, lon]));

    // Query server for given lat, lon, name
    $.get('search/', {lat: lat, lon: lon, name: name}, function(data){
        if (data.length > 0) {
            $.each(data, function(key, value) {
                // Add the returned rivers geo data to the map
                var river = L.geoJson(value.geojson);

                // Add a popup to the river
                river.bindPopup(value.gnis_name);

                markersLayer.addLayer(river);

                // Add the river data to the table
                $('#river-list > tbody:last')
                  .append($('<tr>')
                    .append($('<td>')
                      .text(value.gnis_name || '')
                    )
                    .append($('<td>')
                      .text(value.name_similarity || '')
                    )
                    .append($('<td>')
                      .text(value.meters)
                    )
                  );
            });
        }
        // Zoom map to fit all added geo objects
        map.fitBounds(markersLayer.getBounds());
    });
}
