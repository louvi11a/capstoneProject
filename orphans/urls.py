from . import views
from django.urls import path
from orphans.views import orphan_view, restore_files

urlpatterns = [
    path('', orphan_view, name='orphans'),
    path('profile/<int:orphanID>/', views.orphan_profile, name='orphan_profile'),
    path('files/<int:file_id>/', views.serve_file, name='serve_file'),
    path('delete_files/', views.delete_files, name='delete_files'),
    path('restore_files/', restore_files, name='restore_files'),

]
