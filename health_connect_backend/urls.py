
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userApp.urls')),
    path('training/', include('trainingApp.urls')),
    path('trainingCandidate/', include('trainingCandidateApp.urls')),
    path('worker/', include('communityHealthWorkApp.urls')),
    path('appointment/', include('appointmentApp.urls')),
    path('exam/', include('examApp.urls')),
    path('result/', include('examResultApp.urls')),
    path('report/', include('reportApp.urls')),
    path('activity/', include('activityApp.urls')),
    path('service/', include('serviceApp.urls')),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)