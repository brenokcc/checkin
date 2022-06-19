from django.urls import path, include
from . import views

urlpatterns = [
    path('start/<str:token>/', views.start),
    path('checkins/<str:token>/', views.checkins),
    path('checkin/<str:token>/<str:token_pessoa>/', views.checkin),
    path('checkin/<str:token>/', views.checkin),
    path('end/<str:uuid>/', views.end),
    path('photos/', views.photos),
    path('', include('sloth.api.urls')),
    path('', include('sloth.app.urls')),
]
