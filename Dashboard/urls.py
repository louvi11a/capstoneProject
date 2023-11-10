from django.urls import path
from .views import Dashboard_view


urlpatterns = [
    path('', Dashboard_view, name='Dashboard'),
]
