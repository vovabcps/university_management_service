from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from .models import *
import university.models

#app_list
from django.contrib import admin

#connection db
from django.db import connection
from django.core.files.storage import FileSystemStorage


import sys

import re

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
    #print(username, password)
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
    return SystemUser.objects.get(user=u)



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
        su= request_user(request)

        inscrito= SystemUserSubject.objects.filter(user=su).first()
        #verificar se o aluno ja esta incrito em cadeiras de um curso
        if not inscrito:
            #curso do aluno
            suCourse= SystemUserCourse.objects.get(user=su)

            #as cadeiras obrigatorias q ele vai ter nesse ano
            courseObrig_subjs= CourseSubject.objects.filter(course=suCourse.course, year=suCourse.anoActual).order_by("semester")

            #quais sao os mini cursos q o aluno vai ter naquele ano
            miniCs= Course_MiniCourse.objects.filter(course=suCourse.course, year=suCourse.anoActual)
            
            #as cadeiras dos mini cursos daquele ano
            miniCursosMinorsSubjs= [] #lista de listas
            miniCursosOthersSubjs= [] #lista de listas
            for miniC in miniCs:
                if len(miniC.semestres) == 1 :
                    miniCsubjs= CourseSubject.objects.filter(course=miniC.miniCourse, year=suCourse.anoActual, semester=int(miniC.semestres))
                else:
                    miniCsubjs= CourseSubject.objects.filter(course=miniC.miniCourse, year=suCourse.anoActual).order_by("semester")
                if miniC.miniCourse.grau == "Minor" :
                    miniCursosMinorsSubjs.append([miniC, miniCsubjs])
                else:
                    miniCursosOthersSubjs.append([miniC, miniCsubjs])

            dicMinorsAndOthers = {'others': miniCursosOthersSubjs, 'minors': miniCursosMinorsSubjs}
            course_subjs = {'courseObrig_subjs':courseObrig_subjs, 'miniCs_subjs':dicMinorsAndOthers}
            return render(request, 'student/inscricoes_subject.html', {'suCourse': suCourse, 'course_subjs':course_subjs})
        else: 
            messages.error(request, "Ja esta incrita nas cadeiras do seu curso deste ano!")
            return HttpResponseRedirect(reverse('home_s'))
    else: 
        return HttpResponseRedirect(reverse('login'))


def choose_lessons_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        if request.method == 'POST':
            subjsNameSemestre = request.POST.getlist('subjsNameSemestre') #vai buscar as q foram escolhidas automaticamente!
            #print(subjsNameSemestre)

            valid= True
            if valid : #se tiver tudo bem
                dic1SemSubjs= {}
                dic2SemSubjs= {}
            

                for subjNameSem in subjsNameSemestre : 
                    dicTypeTurmaLessons= {}
                    #print(subjNameSem)
                    subjName, subjSem= subjNameSem.split("|")
                    #print(subjName, subjSem)
                    SubjObj= Subject.objects.get(name=subjName) 
                    lessons= Lesson.objects.filter(subject=SubjObj).order_by("type").order_by("turma")
                    for l in lessons : 
                        detalhes= l.week_day+","+l.hour+","+l.duration+","+l.subject.name+","+l.type+","+l.room.room_number+"|"
                        if l.type in dicTypeTurmaLessons :
                            novaTurma= True
                            for [turma, lstLessons] in dicTypeTurmaLessons[l.type] : 
                                if turma == l.turma :
                                    #print(lstLessons)
                                    oldList= [[t,ls] for [t,ls] in dicTypeTurmaLessons[l.type] if t != l.turma]
                                    dicTypeTurmaLessons[l.type]= oldList + [[l.turma, lstLessons + detalhes]]
                                    novaTurma= False
                                    break
                            if novaTurma:
                                    dicTypeTurmaLessons[l.type] = dicTypeTurmaLessons[l.type] + [[l.turma, detalhes]]
            
                        else:
                            dicTypeTurmaLessons[l.type] = [[l.turma, detalhes]] #nao por tuplos pq eles sao imutaveis
                    if subjSem == "1" :
                        dic1SemSubjs[SubjObj]= dicTypeTurmaLessons
                    else:
                        dic2SemSubjs[SubjObj]= dicTypeTurmaLessons

                semestre= {"1": dic1SemSubjs, "2": dic2SemSubjs}

                return render(request, 'student/choose_lessons.html', {'subjsSem':semestre})
            else:
                messages.error(request, "Ocorreu um problema!")
                messages.error(request, "qual foi? you will never know muahah")
                return HttpResponseRedirect(reverse('inscricoes_subject_s'))

        else:
            return HttpResponseRedirect(reverse('inscricoes_subject_s'))
    else: 
        return HttpResponseRedirect(reverse('login'))


def inscricoes_confirmacao_s(request):
    #verifica os dados da pag choose_lessons
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        if request.method == 'POST':
            subjsNameSemestre = json.loads(request.body.decode("utf-8"))
            #print(subjsNameSemestre)
            semestre1 = subjsNameSemestre['1semLessons']
            semestre2 = subjsNameSemestre['2semLessons']
            totalLessons= subjsNameSemestre['totalLessons']
            print(semestre1)
            #ex: Produção de Documentos Técnicos|14|TP||Produção de Documentos Técnicos|16|PL||Programação I (LTI)|17|PL||Programação I (LTI)|14|TP||
            #Elementos de Matemática II|21|TP||Introdução às Probabilidades e Estatística|21|T||Introdução às Probabilidades e Estatística|23|TP||
            print(semestre2)
            print(totalLessons)
            subjLessonsSem1= semestre1.split("||")[:-1]
            subjLessonsSem2= semestre2.split("||")[:-1]

            if (len(subjLessonsSem1) + len(subjLessonsSem2)) != totalLessons :
                valid = False
            else:
                valid= True
            
            if valid: #se tiver tudo bem
                sysUser= request_user(request)
                subjLessons= subjLessonsSem1 + subjLessonsSem2
                #inscrever nas cadeiras
                subjNameBefor= None
                for subjLess in subjLessons:
                    subjNameLesson= subjLess.split("|")
                    subjName, turma, type = subjNameLesson
                    if subjName != subjNameBefor :
                        SubjObj= Subject.objects.get(name=subjName) 
                        newSysUSubj= SystemUserSubject(user=sysUser, subject=SubjObj, state=0)
                        newSysUSubj.save()
                        turmas= " "
                        subjNameBefor= subjName

                    turmas= turmas + type + turma + " "
                    newSysUSubj.lessons= turmas
                    newSysUSubj.save()

                return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"message": "fail"}), content_type="application/json")

        else:
            return HttpResponseRedirect(reverse('inscricoes_subject_s'))

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





def apagar_s(request):
    return render(request, 'student/apagar.html', {})


# --------------- teacher ---------------
def home_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/home.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_contacts_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/consult_contacts.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))

    
def consult_details_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/consult_details.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))



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
        #print(app_list)
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


def export_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE) :
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/export.html', {'app_list':[app_list[1]]})
    else: 
        return HttpResponseRedirect(reverse('login'))










       

