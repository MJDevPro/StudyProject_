from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/',include('django.contrib.auth.urls'),name='logout'),
    path('', include('base.urls')),
]
