from . import views
from django.urls import path
from orphans.views import orphan_view
from .views import files_view, upload_file


urlpatterns = [
    path('', orphan_view, name='orphans'),
    path('profile/<int:orphanID>/', views.orphan_profile, name='orphan_profile'),
    path('upload/', upload_file, name='upload'),
    path('files/', files_view, name='files'),

    # path('profile', orphanProfile_view, name='profile'),
    # path('', trash_view, name='trash'),

    # Add other URL patterns related to the 'orphans' app if needed.
]
