from django.conf.urls import patterns, url

from thingstore import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^thing/(?P<thing_id>\d+)/$', views.thing, name='thing'),
    url(r'^user/(?P<username>\w+)/$', views.user, name='user'),
)
