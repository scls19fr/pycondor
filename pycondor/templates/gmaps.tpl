<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
      html, body, #map-canvas {
        height: 100%;
        margin: 0px;
        padding: 0px
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=true"></script>
    <script>

function initialize() {
    var task = 
{{ json_task }};

    function getMaxOfArray(numArray) {
        return Math.max.apply(null, numArray);
    }

    function getMinOfArray(numArray) {
        return Math.min.apply(null, numArray);
    }

    var len = task["Name"].length;

    var flightPlanCoordinates = [];

    var center = new google.maps.LatLng(
        (getMaxOfArray(task["Lat"]) + getMinOfArray(task["Lat"])) / 2.0,
        (getMaxOfArray(task["Lon"]) + getMinOfArray(task["Lon"])) / 2.0
    );

    var mapOptions = {
        zoom: 10,
        center: center,
        mapTypeId: google.maps.MapTypeId.{{ map_type }}
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'),
        mapOptions);

    var turnPoint;
    for (var i = len - 1; i >= 0; i--) {
        var Lat = task["Lat"][i];
        var Lon = task["Lon"][i];
        var Name = task["Name"][i];
        var Alt = task["Altitude"][i];
        var turnPointStrId = (i + 1).toString();
        turnPoint = new google.maps.LatLng(Lat, Lon);
        flightPlanCoordinates.push(turnPoint);
        var marker = new google.maps.Marker({
            position: turnPoint,
            map: map,
            title: turnPointStrId + ": " + Name
        });

        var contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">' + turnPointStrId + ": " + Name + '</h1>'+
            '<div id="bodyContent">'+
            '<dl>'+
            '<dt>Lat: </dt><dd>' + Lat.toString() + '</dd>'+
            '<dt>Lon: </dt><dd>' + Lon.toString() + '</dd>'+
            '<dt>Alt: </dt><dd>' + Alt.toString() + '</dd>'+
            '</dl>'+
            '<dl>'+            
            '<dt>Google search: </dt><dd><a href="https://www.google.fr/?#safe=off&q=' + Name + '">' + Name + '</a></dd>'+
            '</dl>'+
            '</div>'+
            '</div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });

        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
        });


    }

    var flightPath = new google.maps.Polyline({
        path: flightPlanCoordinates,
        geodesic: true,
        strokeColor: '#FF0000',
        strokeOpacity: 1.0,
        strokeWeight: 2
    });






    flightPath.setMap(map);
}

google.maps.event.addDomListener(window, 'load', initialize);

    </script>
  </head>
  <body>
    <div id="map-canvas"></div>
  </body>
</html>
