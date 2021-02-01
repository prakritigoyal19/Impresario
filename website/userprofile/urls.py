from django.urls import path
from django.conf.urls import url
from . import views
# appname='userprofile'
urlpatterns = [
    # path('',views.index,name="index"),
    path('userprofile/create_team/<int:par_id>', views.create_team, name="create_team"),
    path('userprofile/team_request/<int:par_id>', views.team_request, name="team_request"),
    url(r'^ajax/approve_or_reject/$', views.ajax_change_status, name='ajax_change_status')
]
