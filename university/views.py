from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from .models import SystemUser
import university.models

#app_list
from django.contrib import admin




# --------------- login ---------------
def login_page(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect_to_user_home(request)
        return render(request, 'login.html', {})
    elif request.method == "POST":
        return login_user(request)


def redirect_to_user_home(request):
    role = request_user_role(request)
    if role.is_a(university.models.ADMIN_ROLE):
        return HttpResponseRedirect(reverse('home_a'))
    elif role.is_a(university.models.TEACHER_ROLE):
        return HttpResponseRedirect(reverse('home_t'))
    elif role.is_a(university.models.STUDENT_ROLE):
        return HttpResponseRedirect(reverse('home_s'))

    return HttpResponseServerError()


def login_user(request):
    creds = json.loads(request.body.decode("utf-8"))
    print(creds)
    username = creds['username']
    password = creds['password']
    print(username, password)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            print("login")
            login(request, user)
            return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message": "inactive"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"message": "invalid"}), content_type="application/json")


def request_user_role(request):
    u = request.user
    su = SystemUser.objects.get(user=u)
    return su.role


# --------------- logout ---------------
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))






#--------------- all ---------------

def profile(request):
    return render(request, 'profile.html', {})

# --------------- student ---------------
def consult_details_s(request):
    return render(request, 'student/consult_details_s.html', {})

def home_s(request):
    role = request_user_role(request)
    if not role.is_a(university.models.STUDENT_ROLE):
        return redirect_to_user_home(request)
    return render(request, 'student/home.html', {})

def password_alt_s(request):
    return render(request, 'student/password_alt.html', {})


# --------------- teacher ---------------
def consult_details_t(request):
    return render(request, 'teacher/consult_details_t.html', {})

def home_t(request):
    role = request_user_role(request)
    if not role.is_a(university.models.TEACHER_ROLE):
        return redirect_to_user_home(request)
    return render(request, 'teacher/home.html', {})

def password_alt_t(request):
    return render(request, 'teacher/password_alt.html', {})


# --------------- admin ---------------
def home_a(request):
    role = request_user_role(request)
    if not role.is_a(university.models.ADMIN_ROLE):
        return redirect_to_user_home(request)
    return render(request, 'admin/index.html', {})

def consult_details_a(request):
    return render(request, 'admin/consult_details.html', {})

def consult_a(request):
    admin_index = admin.site.index(request)
    app_list = admin_index.context_data['app_list']
    return render(request, 'admin/consult.html', {'app_list':app_list})

def insert_a(request):
    admin_index = admin.site.index(request)
    app_list = admin_index.context_data['app_list']
    return render(request, 'admin/insert.html', {'app_list':app_list})


def password_alt_a(request):
    return render(request, 'admin/password_alt.html', {})


