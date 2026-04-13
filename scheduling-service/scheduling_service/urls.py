from django.urls import path, include

urlpatterns = [
    path('api/', include('scheduling_app.urls')),
    path('', include('scheduling_app.urls')),
 # Fallback for health check
]
