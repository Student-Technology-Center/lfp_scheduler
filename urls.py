from django.conf.urls import url

from lfp_scheduler import views as lfp_views

urlpatterns = [
    url(r'^$', lfp_views.lfp, name='lfp'),
    url(r'^gettoken/$', lfp_views.gettoken, name='gettoken'),
]
