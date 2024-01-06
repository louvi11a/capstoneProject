from django.urls import path
from .views import dashboard_view, sentiment_details, orphanSentiment_detail, SearchView

urlpatterns = [
    path('', dashboard_view, name='Dashboard'),
    path('search/', SearchView.as_view(), name='search'),
    path('sentiment_details/', sentiment_details, name='sentiment_details'),
    path('sentiment_details/profile/<int:orphan_id>/',
         orphanSentiment_detail, name='orphanSentiment_detail'),
    # path('search/', views.search, name='search'),
    # path('search_suggestions/', views.search_suggestions,
    #      name='search_suggestions'),
    # #      name='search_suggestions'),

]
