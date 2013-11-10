import json

from django.http import HttpResponse
from django.db import connection
from fuzzywuzzy import fuzz


def search(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    name = request.GET.get('name')

    # All parameters must be present
    if not all([lat, lon]):
        return HttpResponse(status=400)

    # lat and lon must be able to be coerced to floats
    try:
        lat = float(lat)
        lon = float(lon)
    except(ValueError):
        return HttpResponse(status=400)

    # lat and lon must be within -180 to 180 range
    if not all([-180 < lat < 180, -180 < lon < 180]):
        return HttpResponse(status=400)

    # Compose a postgres point from lat and lon
    point = 'POINT({} {})'.format(lon, lat)

    # Query for the nearest objects to the given lat, lon
    query = \
        """SELECT gnis_id,
                 gnis_name,
                 round(ST_Distance_Sphere(ST_Union(wkb_geometry), ST_GeomFromText(%s, 4269))) as meters,
                 ST_AsGeoJSON(ST_Union(wkb_geometry)) as geojson
           FROM flowline
           WHERE gnis_id IN (SELECT gnis_id
                             FROM flowline
                             WHERE st_dwithin(wkb_geometry, ST_GeomFromText(%s, 4269), 0.025))
           GROUP BY gnis_id,
                    gnis_name
           ORDER BY meters
           LIMIT 10;
        """
    cursor = connection.cursor()
    cursor.execute(query, [point, point])
    rows = cursor.fetchall()

    # Assemble the results into dictionaries and add to a list
    results = []
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        row_dict['geojson'] = json.loads(row_dict['geojson'])
        if row_dict['gnis_name'] and name:
            row_dict['name_similarity'] = fuzz.WRatio(name, row_dict['gnis_name'])
        else:
            row_dict['name_similarity'] = None
        results.append(row_dict)

    return HttpResponse(json.dumps(results), content_type="application/json")
