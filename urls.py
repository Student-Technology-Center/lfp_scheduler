from django.conf.urls import url, include

from lfp_scheduler import views as lfp_views

urlpatterns = [
    url(r'^$', lfp_views.lfp, name='lfp'),
    url(r'^gettoken/$', lfp_views.gettoken, name='gettoken'),
    url(r'^public/$', lfp_views.lfp_public, name='lfp_public'),

    #url(r'^new/$', lfp_views.new_lfp, name='new_lfp'),

    url(r'api/', include('lfp_scheduler.api.urls')),
]
