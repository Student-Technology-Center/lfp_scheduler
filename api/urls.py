from django.conf.urls import url

from lfp_scheduler.api import views as api_views

# wwustc.com/lfp/api/event/ POST or DELETE
# wwustc.com/lfp/api/calendar/ GET

# These will now fetch from outlook

urlpatterns = [
    url(r'^event$', api_views.lfp_api_event, name='lfp_api_event'),
    url(r'^calendar$', api_views.lfp_api_calendar, name='lfp_api_calendar'),
]
