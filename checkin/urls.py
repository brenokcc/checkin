from django.urls import path, include
from .views import checkin, checkins, start, end

urlpatterns = [
    path('start/<str:token>/', start),
    path('checkins/<str:token>/', checkins),
    path('checkin/<str:token>/<str:token_pessoa>/', checkin),
    path('checkin/<str:token>/', checkin),
    path('end/<str:uuid>/', end),
    path('', include('sloth.api.urls')),
    path('', include('sloth.app.urls')),
]
