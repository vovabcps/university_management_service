from django.http import HttpResponse
from django.shortcuts import render

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login


def login(request):
    return render(request, 'login.html', {})


def profile(request):
    return render(request, 'profile.html', {})

# --------------- student ---------------
def consult_details_s(request):
    return render(request, 'student/consult_details_s.html', {})

def home_s(request):
    return render(request, 'student/home.html', {})

def password_alt_s(request):
    return render(request, 'student/password_alt.html', {})


# --------------- teacher ---------------
def consult_details_t(request):
    return render(request, 'teacher/consult_details_t.html', {})

def home_t(request):
    return render(request, 'teacher/home.html', {})

def password_alt_t(request):
    return render(request, 'teacher/password_alt.html', {})


# --------------- admin ---------------
def home_a(request):
    return render(request, 'admin/home.html', {})

def consult_details_a(request):
    return render(request, 'admin/consult_details.html', {})

def consult_students_a(request):
    return render(request, 'admin/consult_students.html', {})

def consult_teachers_a(request):
    return render(request, 'admin/consult_teachers.html', {})

def insert_students_a(request):
    return render(request, 'admin/insert_students.html', {})

def insert_teachers_a(request):
    return render(request, 'admin/insert_teachers.html', {})

def password_alt_a(request):
    return render(request, 'admin/password_alt.html', {})


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
