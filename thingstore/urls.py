from django.conf.urls import patterns, url,include
from django.http import HttpResponseRedirect

from thingstore import views,api

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    # url(r'^login/$', views.login_view, name='login'),
    # url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^thing/(?P<thing_id>\d+)/$', views.thing, name='thing'),
    url(r'^user/(?P<username>\w+)/$', views.user, name='user'),
    
    url(r'^settings/$', lambda x: HttpResponseRedirect('/settings/apikeys')),
    url(r'^settings/personal/$', views.settings_personal, name='settings_personal'),
    url(r'^settings/apikeys/$', views.settings_apikeys, name='settings_apikeys'),
    url(r'^settings/apikeys/add/$', views.settings_apikeys_add, name='settings_apikeys_add'),
    url(r'^settings/apikeys/del/(?P<apikey_id>\d+)/$', views.settings_apikeys_del, name='settings_apikeys_del'),
    
    
    url(r'^api/', include(api.urls)),
)
