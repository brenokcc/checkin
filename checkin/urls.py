from django.urls import path, include
from .views import checkin, start, end

urlpatterns = [
    path('start/', start),
    path('checkin/<str:token>/<str:chave_pessoa>/', checkin),
    path('checkin/<str:token>/', checkin),
    path('end/<str:uuid>/', end),
    path('', include('sloth.api.urls')),
    path('', include('sloth.app.urls')),
]
