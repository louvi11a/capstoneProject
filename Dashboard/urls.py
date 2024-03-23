from django.urls import path
from .views import dashboard_view, sentiment_details, orphanSentiment_detail, intervention_academics, intervention_behavior
from . import views
urlpatterns = [
    path('intervention_behavior/', intervention_behavior,
         name='intervention_behavior'),

    path('api/chart-sentiment/', views.sentiment_chart_view, name='chart_sentiment'),
    path('', dashboard_view, name='Dashboard'),
    #     path('search/', SearchView.as_view(), name='search'),  # Corrected line
    path('sentiment_details/', sentiment_details, name='sentiment_details'),
    path('sentiment_details/profile/<int:orphan_id>/',
         orphanSentiment_detail, name='orphanSentiment_detail'),
    path('intervention_academics/', views.intervention_academics,
         name='intervention_academics'),
    path('intervention_health/', views.intervention_health,
         name='intervention_health'),
    path('intervention_behavior/', views.intervention_behavior,
         name='intervention_behavior'),

]
