from . import views
from django.urls import path
from orphans.views import orphan_view
from .views import files_view


urlpatterns = [
    path('', orphan_view, name='orphans'),
    path('profile/<int:orphanID>/', views.orphan_profile, name='orphan_profile'),
    path('files/<int:file_id>/', views.serve_file, name='serve_file'),
    path('files/', files_view, name='files'),


    # path('profile', orphanProfile_view, name='profile'),
    # path('', trash_view, name='trash'),
    # path('upload/', upload_file, name='upload'),

    # Add other URL patterns related to the 'orphans' app if needed.
]
