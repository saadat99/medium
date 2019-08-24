from django.urls import path, re_path, include
from . import views
from django.contrib.auth import views as auth_views


# app_name = "blog"

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='myapp/login.html')),
    path('', views.index, name='homepage'),
    path('register', views.register, name='register'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('details/<int:id>/', views.post_details, name='details'),
    # re_path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
]