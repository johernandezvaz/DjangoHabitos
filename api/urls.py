from django.urls import path
from api.views import mis_recordatorios

urlpatterns = [
    path('recordatorios/', mis_recordatorios, name = 'Recordatorios'),
]