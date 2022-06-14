from django.urls import path, include
from .views import checkin, start, end

urlpatterns = [
    path('start/', start),
    path('checkin/<str:token_aplicacao>/<str:chave_pessoa>/', checkin),
    path('end/<str:uuid>/', end),
    path('', include('sloth.api.urls')),
    path('', include('sloth.app.urls')),
]
