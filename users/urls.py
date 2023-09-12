from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page_view, name='login'),
    path('Dboard', views.Dboard_view, name='Dboard'),
    # Add other URL patterns related to the 'users' app if needed.
]
