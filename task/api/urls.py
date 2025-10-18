from django.urls import path, include


urlpatterns = [
    path('v1/', include('task.api.v1.urls')),
]