from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('ecourt_home.urls')),
    path('admin/', include('administrator.urls')),
    path('judge/', include('judge.urls')),
    path('lawyer/', include('lawyer.urls')),
    path('citizen/', include('citizen.urls')),
    path('users/', include('users.urls')),
    path('cases/', include('cases.urls')),
    path('notifications/', include('notifications.urls')),
    path('payment/', include('payment.urls'))
]

handler404 = 'ecourt_home.views.error_404_view'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
