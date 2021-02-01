from django.urls import path
from django.conf.urls import url
from . import views
appname='userprofile'

urlpatterns = [
    path('',views.org_tree,name="index"),
    path('scheduling/<int:org_id>',views.orgdetail,name="orgDetail"),
]