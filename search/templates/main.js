function nhdSearch(in_lat, in_lon, in_name) {
    var lat = in_lat || document.getElementById('latitude').value;
    var lon = in_lon || document.getElementById('longitude').value;
    var name = in_name || document.getElementById('name').value;

    // Only continue of both lat and lon are present
    if (!(lat && lon)) {
        return false;
    };

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

        // Update our url to reflect the search performed
        var url_lat = encodeURIComponent(lat);
        var url_lon = encodeURIComponent(lon);
        var url_name = encodeURIComponent(name);
        var new_url = '?lat=' + url_lat +'&lon=' + url_lon +'&name=' + url_name
        window.history.pushState({lat: lat, lon: lon, name: name}, '', new_url);

        // Update our search fields to reflect search parameters
        document.getElementById('latitude').setAttribute("value", lat);
        document.getElementById('longitude').setAttribute("value", lon);
        document.getElementById('name').setAttribute("value", name);
    });
}

// More info: http://css-tricks.com/snippets/javascript/get-url-variables/
// Added decodeURIComponent() to function from above url
function getQueryVariable(variable) {
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return decodeURIComponent(pair[1]);}
       }
       return(false);
}

// Check the url and see if there are any search parameters present.
// If lat and lon are present, do a search.
function checkForSearchParameters() {
    var lat = getQueryVariable('lat');
    var lon = getQueryVariable('lon');
    var name = getQueryVariable('name');
    // If at least lat and lon are present, do a search
    if (lat && lon) {
        nhdSearch(lat, lon, name);
    };
}

// Create our map
var map = L.mapbox.map('map', '{{ MAPBOX_MAP_ID }}')
    .setView([38.754, -97.734], 4);

// Create a layer to hold our geo objects
var markersLayer = L.geoJson().addTo(map);

// If our url has search parameters, perform that search
checkForSearchParameters();
