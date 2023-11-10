from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page_view, name='login'),
    path('settings/', views.settings_view, name='settings'),
    # Add other URL patterns related to the 'users' app if needed.
]
