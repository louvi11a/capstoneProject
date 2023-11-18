from django.urls import path
import behavior
from behavior import views


urlpatterns = [
    # other paths...
    path('add_note/<int:orphan_id>/', views.add_note, name='add_note'),
    # other paths...
]


# urlpatterns = [
#     # other paths...
#     path('prac_notes/', views.prac_notes, name='prac_notes'),
#     # other paths...
