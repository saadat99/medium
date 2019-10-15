from django.urls import path, re_path, include, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views


# app_name = "blog"

urlpatterns = [
    # -- Change Password
    path(
        'accounts/password_change/', auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change.html',
            # success_url=reverse_lazy('password_change_done')
        ),
        name='password_change'
    ),
    # -- Change Password Done
    # TODO
    path(
        'accounts/password_change_done/', auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_done.html',
        ),
        name='password_change_done'
    ),
    path('accounts/profile/<slug:username>/', views.profile, name='profile'),
    path('accounts/profile/follow/<slug:username>/<int:action>/', views.follow, name='follow'),
    path('accounts/settings', views.settings, name='settings'),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='myapp/login.html')),
    # path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html')),
    path('', views.index, name='homepage'),
    path('register', views.register, name='register'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('details/<int:id>/', views.post_details, name='details'),
    # re_path(r'^details/(?P<id>[0-9]{1})/$', views.details, name='details'),
]