from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page_view, name='login'),
    path('settings/', views.settings_view, name='settings'),
    path('update_user_info/', views.update_user_info, name='update_user_info'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_reset/', views.CustomPasswordResetView.as_view(),
         name='password_reset'),

    # Add other URL patterns related to the 'users' app if needed.
]
