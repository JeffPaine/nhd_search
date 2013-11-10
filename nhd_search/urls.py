from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^search/$', 'search.views.search', name='search'),

    url(r'^admin/', include(admin.site.urls)),
)
