from django.contrib import admin
from django.urls import path, include
from users.views import notes_view, settings_view, trash_view, files_view, login_page_view, home_view, Dboard_view, orphan_view

# Import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', login_page_view, name="login"),
    path('users/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('home/', home_view, name='home'),
    path('orphan/', orphan_view, name='orphan'),
    path('notes/', notes_view, name='notes'),
    path('files/', files_view, name='files'),
    path('Dboard/', Dboard_view, name='Dboard'),
    path('trash/', trash_view, name='trash'),
    path('settings/', settings_view, name='settings'),
]

urlpatterns += staticfiles_urlpatterns()
