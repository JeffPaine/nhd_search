from django.conf import settings


def add_mapbox_map_id(request):
    return {'MAPBOX_MAP_ID': settings.MAPBOX_MAP_ID}
