from django.conf.urls import patterns, url,include

from thingstore import views,api

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^thing/(?P<thing_id>\d+)/$', views.thing, name='thing'),
    url(r'^user/(?P<username>\w+)/$', views.user, name='user'),
    
    url(r'^api/', include(api.urls)),
)
