from django.urls import path
from .views import dashboard_view, sentiment_details, orphanSentiment_detail, SearchView

urlpatterns = [
    path('', dashboard_view, name='Dashboard'),
    path('search/', SearchView.as_view(), name='search'),  # Corrected line
    path('sentiment_details/', sentiment_details, name='sentiment_details'),
    path('sentiment_details/profile/<int:orphan_id>/',
         orphanSentiment_detail, name='orphanSentiment_detail'),
    # Remove the commented-out paths if they are not needed
]
