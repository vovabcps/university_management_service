from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from .models import SystemUser
import university.models

#app_list
from django.contrib import admin

#connection db
from django.db import connection
from django.core.files.storage import FileSystemStorage


import sys


#password change
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect


#--------------------- all in common -----------------------

def password_change(request):
    u = request.user
    if u.is_authenticated:
        su = SystemUser.objects.get(user=u)
        roleName = su.role.role

        current_url = request.resolver_match.view_name

        if (roleName == "Admin") :
            if current_url != "password_change_a" : 
                return HttpResponseRedirect(reverse('password_change_a'))
            base_template = "admin/base_site.html"
        elif (roleName == "Professor") :
            if current_url != "password_change_t" : 
                return HttpResponseRedirect(reverse('password_change_t'))
            base_template = "teacher/base_t.html"
        else :
            if current_url != "password_change_s" : 
                return HttpResponseRedirect(reverse('password_change_s'))
            base_template = "student/base_s.html"
        

        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Your password was successfully updated!')
                #return redirect('password_change_a') #se correr bem
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'password_alt.html', {'form': form, 'roleName': roleName, 'base_template':base_template}) #se correr mal
    else: 
        return HttpResponseRedirect(reverse('login'))


def is_authenticated(request, role_name):
    u = request.user
    if u.is_authenticated:
        su = SystemUser.objects.get(user=u)
        role= su.role
        return role.is_a(role_name)
    return False

# --------------- login ---------------
def login_page(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect_to_user_home(request)
        return render(request, 'login.html', {})
    elif request.method == "POST":
        return login_user(request)


def redirect_to_user_home(request):
    su= request_user(request)
    role = su.role
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


def request_user(request):
    u = request.user
    su = SystemUser.objects.get(user=u)
    return su


# --------------- logout ---------------
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


# --------------- student ---------------
def home_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/home.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def inscricoes_subject_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/inscricoes_subject.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_contacts_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/consult_contacts.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_details_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/consult_details.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_subjects_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/consult_subjects.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_university_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/consult_university.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))




# --------------- teacher ---------------
def consult_details_t(request):
    return render(request, 'teacher/consult_details_t.html', {})

def home_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/home.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))



def password_alt_t(request):
    return render(request, 'teacher/password_alt.html', {})


# --------------- admin ---------------
def home_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        return render(request, 'admin/index.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/consult.html', {'app_list':app_list})
    else: 
        return HttpResponseRedirect(reverse('login'))

def consult_auth_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/consult.html', {'app_list':[app_list[0]]})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_uni_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/consult.html', {'app_list':[app_list[1]]})
    else: 
        return HttpResponseRedirect(reverse('login'))

def insert_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/insert.html', {'app_list':app_list})
    else: 
        return HttpResponseRedirect(reverse('login'))


        
    

def operacoesBloco_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        if request.method == 'POST':
            if request.FILES.get('file_sql', False):
                valid= "yapp"
                myfile = request.FILES['file_sql']

                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile) # saves the file to `media` folder
                uploaded_file_url = fs.url(filename) # gets the url

                with connection.cursor() as cursor:
                    try:
                        for line in open(uploaded_file_url):
                            if line != "\n" and len(line) > 5 and line[0] != "-": #para ignorar as linhas em branco ou so com espaços ou start with '-'
                                cursor.execute(line)
                    except Exception as e:
                        messages.error(request, "O ficheiro contem erros!")
                        valid = "error"  

                fs.delete(myfile.name)



            else:
                valid= "empty"
            return render(request, 'admin/oper_bloco.html', {'uploaded': valid})
        elif request.method == 'GET':
            return render(request, 'admin/oper_bloco.html')
    else: 
        return HttpResponseRedirect(reverse('login'))

       

