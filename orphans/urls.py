from django.urls import path
from . import views
from orphans.views import orphan_view, restore_files, file_details, family_detail
from orphanage_system import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
print(views.__file__)

urlpatterns = [
    path('files/', views.files_view, name='files'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('rename_file/', views.rename_file, name='rename_file'),
    path('delete_files/', views.delete_files, name='delete_files'),
    path('restore_files/', restore_files, name='restore_files'),
    path('', orphan_view, name='orphans'),

    path('profile/<int:orphanID>/',
         views.orphan_profile, name='orphan_profile'),
    path('profile/<int:orphan_id>/academic/',
         views.academic_profile, name='academic_profile'),
    path('profile/<int:orphan_id>/health/',
         views.health_profile, name='health_profile'),
    path('orphan/<int:orphan_id>/add_bmi/',
         views.add_bmi, name='add_bmi'),
    path('profile/<int:orphan_id>/bmi/',
         views.bmi_profile, name='bmi_profile'),
    path('profile/<int:orphan_id>/behavior/',
         views.behavior_profile, name='behavior_profile'),


    path('family/<int:family_id>/', family_detail, name='family_detail'),

    path('files/details/<int:file_id>/', views.file_details,
         name='file_details'),  # Add this line

    path('files/<int:file_id>/', views.serve_file, name='serve_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete/<int:file_id>/', views.delete_files, name='delete_files'),

    # path('add_orphan/', views.add_orphan, name='add_orphan'),

    path('delete_orphan/<int:orphan_id>/',
         views.delete_orphan, name='delete_orphan'),
    path('edit_orphan/<int:orphan_id>/', views.edit_orphan, name='edit_orphan'),
    path('save_changes/<int:orphan_id>/',
         views.save_changes, name='save_changes'),
    path('add_orphan/', views.addOrphanForm, name='add_orphan'),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL,
                                                  document_root=settings.MEDIA_ROOT)
