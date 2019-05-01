from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
    re_path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
]