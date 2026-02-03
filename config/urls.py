# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse
from django.views import View


class RootView(View):
    def get(self, request):
        return JsonResponse({
            'message': 'Habit Tracker API',
            'version': '1.0.0',
            'docs': '/api/docs/',
            'admin': '/admin/'
        })


urlpatterns = [
    #Админка
    path('admin/', admin.site.urls),

    #API документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    #API маршруты
    path('api/', include('users.urls')),  # users.urls будет начинаться с api/
    path('api/', include('habits.urls')), # habits.urls будет начинаться с api/
    path('', RootView.as_view(), name='root'),
]