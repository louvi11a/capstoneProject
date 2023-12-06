from django import views
from django.urls import path
from . import views
from .views import dashboard_view


urlpatterns = [
    path('', dashboard_view, name='Dashboard'),
    path('search/', views.search, name='search'),
    path('search_suggestions/', views.search_suggestions,
         name='search_suggestions'),
    #      name='search_suggestions'),

]