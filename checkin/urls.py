from django.urls import path, include
from . import views

urlpatterns = [
    path('start/<str:token>/', views.start),
    path('profile/<str:token>/', views.profile),
    path('checkin/<str:tipo>/<str:token>/<str:token2>/', views.checkin),
    path('checkin/<str:tipo>/<str:token>/', views.checkin),
    path('end/<str:uuid>/', views.end),
    path('upload/<str:uuid>/', views.upload),
    path('solicitar/', views.solicitar),
    path('', include('sloth.api.urls')),
    path('', include('sloth.app.urls')),
]
