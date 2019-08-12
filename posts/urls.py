from django.urls import path, re_path
from . import views

# app_name = "blog"

urlpatterns = [
    path('', views.index, name='homepage'),
    path('register', views.register, name='register'),
    path('logout', views.logout_request, name='logout'),
    path('login', views.login_request, name='login'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('details/<int:id>/', views.post_details, name='details'),
    # re_path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
]