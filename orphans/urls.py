from django.urls import path
from . import views
# from orphans.views import orphan_view, restore_files, file_details, family_detail, add_health_details, filter_orphans
from orphanage_system import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

print(views.__file__)

urlpatterns = [

    path('filter_orphans/', views.filter_orphans, name='filter_orphans'),
    path('files/orphan_files/<int:file_id>/',
         views.serve_orphan_files, name='serve_orphan_files'),
    path('files/serve/<int:file_id>/', views.serve_file, name='serve_file'),

    path('delete-permanent/', views.permanent_file_deletion,
         name='permanent_file_deletion'),

    path('add-health-details/', views.add_health_details,
         name='add_health_details'),

    #     path('upload_birth_certificate/<int:orphan_id>/',
    #          views.upload_birth_certificate, name='upload_birth_certificate'),

    path('search_orphans/', views.Orphan_Search.as_view(), name='search_orphans'),
    path('search_files/', views.File_Search.as_view(), name='search_files'),

    path('add_note/<int:orphan_id>/', views.add_note, name='add_note'),
    path('files/', views.files_view, name='files_view'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('rename_file/', views.rename_file, name='rename_file'),

    path('delete_files/', views.delete_files, name='delete_files'),
    path('restore_files/', views.restore_files, name='restore_files'),
    path('', views.orphan_view, name='orphans'),
    path('add_orphan/', views.addOrphanForm, name='add_orphan'),

    path('orphan_profile/<int:orphanID>/',
         views.orphan_profile, name='orphan_profile'),

    path('profile/<int:orphan_id>/academic/',
         views.academic_profile, name='academic_profile'),
    path('save_academic_details/<int:orphan_id>/',
         views.save_academic_details, name='save_academic_details'),

    path('profile/<int:orphan_id>/health/',
         views.health_profile, name='health_profile'),

    path('orphan/<int:orphan_id>/add_bmi/',
         views.add_bmi, name='add_bmi'),
    path('profile/<int:orphan_id>/bmi/',
         views.bmi_profile, name='bmi_profile'),
    path('profile/<int:orphan_id>/behavior/',
         views.behavior_profile, name='behavior_profile'),


    path('family/<int:family_id>/', views.family_detail, name='family_detail'),

    path('files/details/<int:file_id>/', views.file_details,
         name='file_details'),
    path('files/details/<int:file_id>/',
         views.file_details, name='file_details'),

    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete/<int:file_id>/', views.delete_files, name='delete_files'),

    # path('add_orphan/', views.add_orphan, name='add_orphan'),

    path('delete_orphan/<int:orphan_id>/',
         views.delete_orphan, name='delete_orphan'),
    path('edit_orphan/<int:orphan_id>/', views.edit_orphan, name='edit_orphan'),
    path('save_changes/<int:orphan_id>/',
         views.save_changes, name='save_changes'),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL,
                                                  document_root=settings.MEDIA_ROOT)
