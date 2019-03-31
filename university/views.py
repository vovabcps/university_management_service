from django.shortcuts import render

#convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

def home(request):
    return render(request, 'home.html', {})