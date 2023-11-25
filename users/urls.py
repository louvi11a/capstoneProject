from django.urls import path
from . import views
from .views import update_user_info
urlpatterns = [
    path('', views.login_page_view, name='login'),
    path('settings/', views.settings_view, name='settings'),
    path('update_user_info/', update_user_info, name='update_user_info'),
    path('change_password/', views.change_password, name='change_password'),
    # Add other URL patterns related to the 'users' app if needed.
]
