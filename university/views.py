from django.http import HttpResponse
from django.shortcuts import render

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login


def home(request):
    return render(request, 'home.html', {})


def login_user(request):
    creds = json.loads(request.body.decode("utf-8"))
    username = creds['username']
    password = creds['password']
    print(username, password)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message": "inactive"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"message": "invalid"}), content_type="application/json")
