from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shopee.urls')),
    path(r'session_security/', include('session_security.urls')),
    path("admin/", include('loginas.urls')),
]

handler404 = 'shopee.views.error_404'
handler500 = 'shopee.views.error_500'
handler403 = 'shopee.views.error_403'
handler400 = 'shopee.views.error_400'


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
