from django.urls import path, re_path
from . import views

app_name = "posts"

urlpatterns = [
    path('', views.index, name='homepage'),
    path('register', views.register, name='register'),
    path('logout', views.logout_request, name='logout'),
    path('login', views.login_request, name='login'),
    # path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
    re_path(r'^details/(?P<id>[0-9]{1})/$', views.details, name
    ='details'),
]