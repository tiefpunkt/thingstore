from django.conf.urls import patterns, url,include

from thingstore import views

from tastypie.api import Api
from thingstore.api import ThingResource, MetricResource

v1_api = Api(api_name='v1')
v1_api.register(ThingResource())
v1_api.register(MetricResource())

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^thing/(?P<thing_id>\d+)/$', views.thing, name='thing'),
    url(r'^user/(?P<username>\w+)/$', views.user, name='user'),
    
    url(r'^api/', include(v1_api.urls)),
)
