from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from . import views
urlpatterns = [

    path('save_intervention/<int:orphan_id>/',
         views.save_intervention, name='save_intervention'),
    path('intervention_academics/', views.intervention_academics,
         name='intervention_academics'),
    path('get_orphan_health_data/<int:orphan_id>/',
         views.get_orphan_health_data, name='get_orphan_health_data'),


    path('overall_gpa_summary/',
         views.overall_gpa_summary, name='overall_gpa_summary'),
    path('individual_gpa_summary/<int:orphan_id>/',
         views.individual_gpa_summary, name='individual_gpa_summary'),





    path('overall_behavior_summary/',
         views.overall_behavior_summary, name='overall_behavior_summary'),

    path('individual_behavior_summary/<int:orphan_id>/',
         views.individual_behavior_summary, name='individual_behavior_summary'),

    path('get_orphan_bmi_data/<int:orphan_id>/',
         views.get_orphan_bmi_data, name='get_orphan_bmi_data'),

    path('overall_analysis/',
         views.overall_analysis, name='overall_analysis'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('intervention_behavior/', views.intervention_behavior,
         name='intervention_behavior'),

    path('api/chart-sentiment/', views.sentiment_chart_view, name='chart_sentiment'),

    path('', views.dashboard_view, name='Dashboard'),
    path('sentiment_details/', views.sentiment_details, name='sentiment_details'),
    path('sentiment_details/profile/<int:orphan_id>/',
         views.orphanSentiment_detail, name='orphanSentiment_detail'),


    path('intervention_health/', views.intervention_health,
         name='intervention_health'),


    path('chart_behavior/', views.chart_behavior, name='chart_behavior'),
    path('chart_bmi/', views.chart_bmi, name='chart_bmi'),
    path('chart_age/', views.chart_age, name='chart_age'),
    path('chart_health/', views.chart_health, name='chart_health'),
    path('chart_academic/', views.chart_academic, name='chart_academic'),

]
