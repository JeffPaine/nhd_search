import json

from django.http import HttpResponse

from . import utils


def search(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    name = request.GET.get('name')

    # geo parameters must be present
    if not all([lat, lon]):
        return HttpResponse(status=400)

    results = utils.search_nhd(name, lat, lon, limit=10)

    return HttpResponse(json.dumps(results), content_type="application/json")
