from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/(?P<user_id>\d+)/$', views.UserProfileView.as_view(), name='user_profile'),
]