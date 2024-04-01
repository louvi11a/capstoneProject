from django import views
from django.contrib import admin
from django.urls import path, include
from orphanage_system import settings
# from users.views import notes_view, settings_view, trash_view, files_view, login_page_view, home_view, orphan_view
from users.views import login_page_view
from orphans.views import trash_view
# from behavior.views import add_note
# Import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from orphanage_system import settings
from users.views import settings_view

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', login_page_view, name="login"),
    path('auth/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('orphans/', include('orphans.urls')),
    path('behavior/', include('behavior.urls')),
    path('Dashboard/', include('Dashboard.urls')),
    path('settings/', settings_view, name='settings'),
    path('files/deleted_files/', trash_view, name='trash_view'),

]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL,
                                                  document_root=settings.MEDIA_ROOT)
