from django.urls import path
from . import views


urlpatterns = [
    path('',views.org_tree,name="index"),
    path('scheduling/<int:org_id>',views.orgdetail,name="orgDetail"),
]