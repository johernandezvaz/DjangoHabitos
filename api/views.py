from django.shortcuts import render
from habitos.models import Recordatorio
from django.http import JsonResponse
from django.core import serializers

# Create your views here.
def mis_recordatorios(request):
    queryset = Recordatorio.objects.all()
    json = serializers.serialize("json", queryset)
    return JsonResponse(json, safe=False)