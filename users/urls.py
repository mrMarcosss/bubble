from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/(?P<user_id>\d+)/$', views.UserProfileView.as_view(), name='user_profile'),
    url(r'^settings/$', views.UserSettings.as_view(), name='settings'),
]