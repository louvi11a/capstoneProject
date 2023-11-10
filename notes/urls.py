from django.urls import path
import notes
from notes import views

urlpatterns = [
    # other paths...
    path('notes/', views.notes, name='notes'),
    # other paths...
]
