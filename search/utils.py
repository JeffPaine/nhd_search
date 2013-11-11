import json
import operator
import os

import postgres
from fuzzywuzzy import fuzz


def search_nhd(name, lat, lon, limit=10):
    """Search the National Hydrograpy Dataset (stored in postgres)"""

    # lat and lon must be able to be coerced to floats
    try:
        lat = float(lat)
        lon = float(lon)
    except(ValueError):
        return None

    # lat and lon must be within the -180 to 180 range
    if not all([-180 < lat < 180, -180 < lon < 180]):
        return None

    # We're using postgres.py and the DATABASE_URL environment variable so we
    # can maximize the reusability of this code
    db = postgres.Postgres(os.environ.get('DATABASE_URL'))

    # Query for the nearest objects to the given lat, lon
    query = \
        """SELECT gnis_id,
                 gnis_name,
                 round(ST_Distance_Sphere(ST_Union(wkb_geometry), ST_SetSRID(ST_Point(%(lon)s, %(lat)s), 4269))) as meters,
                 ST_AsGeoJSON(ST_Union(wkb_geometry)) as geojson
           FROM flowline
           WHERE gnis_id IN (SELECT gnis_id
                             FROM flowline
                             WHERE st_dwithin(wkb_geometry, ST_SetSRID(ST_Point(%(lon)s, %(lat)s), 4269), 0.025))
           GROUP BY gnis_id,
                    gnis_name
           ORDER BY meters
           LIMIT %(limit)s;
        """
    query_dict = {'lat': lat, 'lon': lon, 'limit': limit}
    nearest_rivers = db.all(query, query_dict)

    # If there's no matches, return None
    if len(nearest_rivers) == 0:
        return None

    # Convert the returned records into a list of dictionaries
    rivers = [r._asdict() for r in nearest_rivers]
    for r in rivers:
        # Change the geojson string into a proper dictionary
        r['geojson'] = json.loads(r['geojson'])
        if name and r['gnis_name']:
            # Calculate name similarity of the search name and river name
            r['name_similarity'] = fuzz.WRatio(name, r['gnis_name'])
        else:
            r['gnis_name'] = None

    return sorted(rivers, key=operator.itemgetter('meters'))[:limit]
