from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User
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

#consult details
from django.core.validators import validate_email

#date django model
from datetime import datetime

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



# -------------------------------------------------- logout --------------------------------------------------
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

# --------------------------------------------------------------------------------------------------------------------------------
#                                                        student
# --------------------------------------------------------------------------------------------------------------------------------

def home_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        inscrito = list(SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj))
       # print(inscrito)

        suCourse = SystemUserCourse.objects.get(user=su).course

        regentes = []
        for sub in inscrito:
            if PersonalInfo.objects.filter(user=sub.subject.regente).first() not in regentes:
                regentes.append(PersonalInfo.objects.filter(user=sub.subject.regente).first())

        return render(request, 'student/home.html', {"suAllSubjects": inscrito, "suRegentes": regentes })
    else: 
        return HttpResponseRedirect(reverse('login'))


def inscricoes_subject_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        su= request_user(request)
        schoolYearObj= SchoolYear.objects.get(begin=2018)
        inscrito= SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj).first()

        #verificar se o aluno ja esta incrito em cadeiras de um curso
        if not inscrito:
            #cadeiras que ele nao se pode inscrever pq ja foi aprovado
            SystemUserSubjectObjs= SystemUserSubject.objects.filter(user=su, state=1) #qd se esta a increver nao a pending(ou foi aprovado ou reprovou)
            subjsAprov= []
            for SystemUSubjectObj in SystemUserSubjectObjs :
                subjsAprov.append(SystemUSubjectObj.subject)
            print(len(subjsAprov))

            #curso do aluno
            suCourse= SystemUserCourse.objects.get(user=su)
            
            anosCreditos= suCourse.course.credits_numberByYear #1:60|2:60|3:60
            lstAnoCred= anosCreditos.split("|")
            dicAnoSubjs= {}

            for anoCred in lstAnoCred:
                ano, cred = anoCred.split(":")
                credFeitosAno= 0
                credFeitosSubjsObrig= 0
                credTotalTroncoComum= 0

                #as cadeiras obrigatorias q ele vai ter nesse ano
                courseObrig_subjs= CourseSubject.objects.filter(course=suCourse.course, year=int(ano)).order_by("semester")

                #as cadeiras obrigatorias que ele ainda n foi aprovado
                courseObrig_subjsPorFazer= []
                for courseObrig_subj in courseObrig_subjs:
                    credTotalTroncoComum += courseObrig_subj.subject.credits_number
                    if courseObrig_subj.subject not in subjsAprov :
                        courseObrig_subjsPorFazer.append(courseObrig_subj)
                    else: #se ele ja fez a cadeira
                        print(courseObrig_subj.subject.name)
                        credFeitosSubjsObrig += courseObrig_subj.subject.credits_number

                subjsObrig= [credTotalTroncoComum, credFeitosSubjsObrig, courseObrig_subjsPorFazer]
                credFeitosAno += credFeitosSubjsObrig

                #quais sao os mini cursos q o aluno vai ter naquele ano
                miniCs= Course_MiniCourse.objects.filter(course=suCourse.course, year=int(ano))

                #as cadeiras dos mini cursos daquele ano
                miniCursosOthersSubjs= [] #lista de listas, todos os mini cursos exepto minors
                minor= []
                for miniC in miniCs:
                    credNecessarios= miniC.credits_number
                    credFeitos=0
                    if miniC.miniCourse.grau != "Minor":
                        if len(miniC.semestres) == 1 :
                            miniCsubjs= CourseSubject.objects.filter(course=miniC.miniCourse, year=ano, semester=int(miniC.semestres))
                        else:
                            miniCsubjs= CourseSubject.objects.filter(course=miniC.miniCourse, year=ano).order_by("semester")

                        #remover as cadeiras em q o aluno ja foi aprovado
                        miniCsubjsPorFazer= []
                        for miniCsubj in miniCsubjs:
                            if miniCsubj.subject not in subjsAprov :
                                miniCsubjsPorFazer.append(miniCsubj)
                            else:
                                print(miniCsubj.subject.name)
                                credFeitos += miniCsubj.subject.credits_number

                        if credFeitos < credNecessarios : #se ele ainda tem cred para fazer do mini curso
                            miniCursosOthersSubjs.append([miniC, credFeitos, miniCsubjsPorFazer])
                        else: #se ele ja completou o minicurso
                            miniCursosOthersSubjs.append([miniC, credFeitos, []])

                    #se naquele curso e naquele ano houver minor e ele foi admitdo
                    elif miniC.miniCourse.name == suCourse.minor :
                            miniCsubjs= CourseSubject.objects.filter(course=miniC.miniCourse, year=ano).order_by("semester") 
                            minor= [[miniC, credFeitos, miniCsubjs]]
                    
                    credFeitosAno += credFeitos
   
                dicMinorsAndOthers = {'others': miniCursosOthersSubjs, 'minor': minor}
                course_subjs = {'courseObrig_subjs':subjsObrig, 'miniCs_subjs':dicMinorsAndOthers}

                # se ele ainda tiver cadeiras para fazer neste ano:
                #if len(minor) != 0 or len(miniCursosOthersSubjs) != 0 or len(courseObrig_subjsPorFazer) != 0 :
                dicAnoSubjs[ano + "º ano"] = {'ceditos': [credFeitosAno, cred] , 'course_subjs': course_subjs}

            return render(request, 'student/inscricoes_subject.html', {'suCourse': suCourse, 'dicAnoSubjs':dicAnoSubjs})
        else: 
            messages.error(request, "Ja esta inscrito/a nas cadeiras do seu curso deste ano!")
            return HttpResponseRedirect(reverse('home_s'))
    else: 
        return HttpResponseRedirect(reverse('login'))


def choose_lessons_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        if request.method == 'POST':
            valid= True
            print(request.POST)  #so vai buscar as q foram escolhidas!

            if len(request.POST) == 0 : #se nao escolher nenhuma cadeira
                valid= False
                messages.error(request, "Escolha pelo menos uma cadeira!!")

            subjsNameEscolhidas= []
            subjsEscolhidas= []
            credTotaisEscolhidos= 0
            for anoCourseCredTotalCredFeitos in list(request.POST.keys()) : 
                ano, course, credTotais, credFeitos= anoCourseCredTotalCredFeitos.split("|")
                credTotaisSubj= 0
                for subjSemCred in request.POST.getlist(anoCourseCredTotalCredFeitos) :
                    #print(anoCourseCredTotalCredFeitos + ": " + subjSemCred)
                    subjsEscolhidas.append(subjSemCred)
                    subj, sem, cred= subjSemCred.split("|")
                    subjsNameEscolhidas.append(subj)
                    credTotaisEscolhidos += int(cred)
                    credTotaisSubj += int(cred)
                
                if  credTotaisSubj + int(credFeitos) > int(credTotais) :
                    valid= False
                    messages.error(request, "Não pode ultrapassar os " + credTotais + " cred. de " + course + " do " + ano)
                    

            if credTotaisEscolhidos > 72 :
                valid= False
                messages.error(request, "Não pode ultrapassar os 72 creditos!!!")
            
            if escolheu_a_msm_subj_mais_q_uma_vez(subjsNameEscolhidas):
                valid= False
                messages.error(request, "So pode escolher 1 vez a mesma cadeira!!")

            if valid : #se tiver tudo bem
                dic1SemSubjs= {}
                dic2SemSubjs= {}

                for subjNameSem in subjsEscolhidas : 
                    dicTypeTurmaLessons= {}
                    #print(subjNameSem)
                    subjName, subjSem, subCred= subjNameSem.split("|")
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
                return HttpResponseRedirect(reverse('inscricoes_subject_s'))

        else:
            return HttpResponseRedirect(reverse('inscricoes_subject_s'))
    else: 
        return HttpResponseRedirect(reverse('login'))

def escolheu_a_msm_subj_mais_q_uma_vez(lst):
    return len(lst) != len(set(lst))

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
                subjLessons= [subjLessonsSem1, subjLessonsSem2]
                schoolYearObj= SchoolYear.objects.get(begin=2018)
                #inscrever nas cadeiras
                subjNameBefor= None
                sem= 1
                for subjLessonsSem in subjLessons:
                    for subjLess in subjLessonsSem:
                        subjNameLesson= subjLess.split("|")
                        subjName, turma, type = subjNameLesson
                        if subjName != subjNameBefor :
                            SubjObj= Subject.objects.get(name=subjName) 
                            newSysUSubj= SystemUserSubject(user=sysUser, subject=SubjObj, state=0, subjSemestre=sem, anoLetivo=schoolYearObj)
                            newSysUSubj.save()
                            turmas= " "
                            subjNameBefor= subjName

                        turmas= turmas + type + turma + " "
                        newSysUSubj.turmas= turmas
                        newSysUSubj.save()
                    sem += 1

                return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"message": "fail"}), content_type="application/json")

        else:
            return HttpResponseRedirect(reverse('inscricoes_subject_s'))

    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_contacts_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :

        class FearAllWhoCodeThis:

            def __init__(self, tab_name, sub_name, classes_students):
                self.id = "#"+tab_name
                self.idNoHashTag = tab_name
                self.subjectName = sub_name
                self.classes = classes_students

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        i = 1
        turmaLessons = []

        finalList = []

        suSubjs = SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj)

        for suSubj in suSubjs:
            subj = suSubj.subject
            sem = suSubj.subjSemestre
            lstTurmas = suSubj.turmas.split(" ")
            # ex: lstTurmas-> ["T11","TP13","PL13"]
            lstTurmasSemEspaços = [e for e in lstTurmas if e != ""]

            myListOfTuples =[]
            for typeTurma in lstTurmasSemEspaços:
                #subjSemestre = sem

                myList = list(SystemUserSubject.objects.filter(subject=subj, turmas__contains=typeTurma, anoLetivo=schoolYearObj, subjSemestre=sem))
                print(typeTurma)
                print(subj.name)

                myListOfCollegues=[]
                for line in myList:
                    myListOfCollegues.append(PersonalInfo.objects.get(user=line.user))
                print(myListOfCollegues)
                myListOfTuples.append((typeTurma, myListOfCollegues))

            finalList.append(FearAllWhoCodeThis("tab" + str(i), subj.name, myListOfTuples))
            i+=1

        return render(request, 'student/consult_contacts.html', {"finalList":finalList})
    else: 
        return HttpResponseRedirect(reverse('login'))



def consult_details_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        consult_details_post(request)
        return render(request, 'student/consult_details.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_subjects_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        inscrito = list(SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj))
        # print(inscrito)

        suCourse = SystemUserCourse.objects.get(user=su).course
        allMyCourseSubj = list(CourseSubject.objects.filter(course=suCourse))

        miniCs = Course_MiniCourse.objects.filter(course=suCourse)
        print(miniCs)

        nameBefore= []
        for mC in miniCs:
            if mC.miniCourse.name not in nameBefore:
                if mC.miniCourse.grau != "Minor":
                    tempVar = CourseSubject.objects.filter(course=mC.miniCourse)
                    allMyCourseSubj = allMyCourseSubj + list(tempVar)
            nameBefore.append(mC.miniCourse.name)

        regentes = []

        for sub in inscrito:
            if PersonalInfo.objects.filter(user=sub.subject.regente).first() not in regentes:
                regentes.append(PersonalInfo.objects.filter(user=sub.subject.regente).first())

        return render(request, 'student/consult_subjects.html', {"suAllSubjects": inscrito, "suRegentes": regentes, "allMyCourseSubj": allMyCourseSubj})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_presencas_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/consult_presenças.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def consult_university_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        listaFacs = list(Faculdade.objects.all())
        return render(request, 'student/consult_university.html', {"listaFaculdades": listaFacs})
    else: 
        return HttpResponseRedirect(reverse('login'))


def request_change_lesson_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/request_change_lesson.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))

def estado_pedidos_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE) :
        return render(request, 'student/estado_pedidos.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def apagar_s(request):
    return render(request, 'student/apagar.html', {})

# --------------------------------------------------------------------------------------------------------------------------------
#                                                        teacher
# --------------------------------------------------------------------------------------------------------------------------------

def home_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        inscrito = list(Lesson.objects.filter(professor=su))
        # print(inscrito)
        mySubjects = []
        my_dictionary = {} #key:cadeira, value: turmas em q ele da aulas dessa cadeira

        for subj in inscrito:
            if subj.subject not in list(my_dictionary.keys()):
                my_dictionary[subj.subject] = ""
                mySubjects.append(subj.subject)

            if (subj.type + subj.turma) not in my_dictionary[subj.subject]:
                my_dictionary[subj.subject] = my_dictionary[subj.subject] + subj.type + subj.turma +" "

        for subj in mySubjects:
            my_dictionary[subj] = my_dictionary[subj][:-1]


        regentes = []
        for sub in inscrito:
            if PersonalInfo.objects.filter(user=sub.subject.regente).first() not in regentes:
                regentes.append(PersonalInfo.objects.filter(user=sub.subject.regente).first())


        return render(request, 'teacher/home.html', {"suRegentes": regentes, "typesAndLessons" : my_dictionary})
    else: 
        return HttpResponseRedirect(reverse('login'))



def consult_contacts_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :

        profRole = Role.objects.get(role="Professor")
        AllTeachers = SystemUser.objects.filter(role=profRole)
        AllTeachersProfiles = []

        for prof in AllTeachers:
            endmeplz = Subject.objects.filter(regente=prof)
            subReg = ", ".join(([sub.name for sub in endmeplz]))

            if len(subReg) == 2:
                subReg=""

            AllTeachersProfiles.append((PersonalInfo.objects.get(user=prof), subReg))

        return render(request, 'teacher/consult_contacts.html', {"Teachers": AllTeachersProfiles})
    else: 
        return HttpResponseRedirect(reverse('login'))


    
def consult_details_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        consult_details_post(request)
        return render(request, 'teacher/consult_details.html', {})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_turmas_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        if request.method == 'GET':
            su = request_user(request)
            suLessons = list(Lesson.objects.filter(professor=su))
            schoolYearObj = SchoolYear.objects.get(begin=2018)

            dic1SemSubjs= {}
            dic2SemSubjs= {}

            for lesson in suLessons:
                str= lesson.type + lesson.turma
                subj= lesson.subject
                CRsubjs= CourseSubject.objects.filter(subject=subj) 

                #por a cadeira na listaSemestre certo com as respetivas Turmas

                #se o sem da cadeira e igual independentemente do curso
                if is_semestres_all_same(CRsubjs) :
                    sem= CRsubjs[0].semester
                    if sem == 1:
                        if subj not in list(dic1SemSubjs.keys()):
                            dic1SemSubjs[subj] = str
                        else:
                            dic1SemSubjs[subj] = dic1SemSubjs[subj] + " " + str
                    else:
                        if subj not in list(dic2SemSubjs.keys()):
                            dic2SemSubjs[subj] = str
                        else:
                            dic2SemSubjs[subj] = dic2SemSubjs[subj] + " " + str
                else:
                    if subj not in list(dic1SemSubjs.keys()):
                        dic1SemSubjs[subj] = str
                    else:
                        dic1SemSubjs[subj] = dic1SemSubjs[subj] + " " + str

                    if subj not in list(dic2SemSubjs.keys()):
                        dic2SemSubjs[subj] = str
                    else:
                        dic2SemSubjs[subj] = dic2SemSubjs[subj] + " " + str
                
            for subj in list(dic1SemSubjs.keys()):
                dic1SemSubjs[subj] = getAlunosOfSubjBySTR(1, subj,  dic1SemSubjs[subj], schoolYearObj)

            for subj in list(dic2SemSubjs.keys()):
                dic2SemSubjs[subj] = getAlunosOfSubjBySTR(2, subj,  dic2SemSubjs[subj], schoolYearObj)

            print(dic1SemSubjs)
            print(dic2SemSubjs)
            semestre= {"1": dic1SemSubjs, "2": dic2SemSubjs}
            return render(request, 'teacher/consult_turmas_D.html', {'subjsSem':semestre})
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)
            alunoFc= dadosJson['aluno']
            print(alunoFc)
            horarioAluno= []
            return HttpResponse(json.dumps({"message": "success", "alunos": horarioAluno}), content_type="application/json")

    else: 
        return HttpResponseRedirect(reverse('login'))

def getAlunosOfSubjBySTR(sem, subj, string, schoolYearObj):
    #ex: 1, AD, " T11 TP12 T14 L15 T11", 2018
    dicTypeTurmasAlunos= {}
    lstTypeTurmas= string.split(" ")
    lstTypeTurmasSemEspaços= [e for e in lstTypeTurmas if e != ""]
    print(lstTypeTurmasSemEspaços)
    lstTypeTurmasSemEspaçosUnique= uniqueElements(lstTypeTurmasSemEspaços)
    print(lstTypeTurmasSemEspaçosUnique)  #[T11, TP12, T14, L15]

    for typeTurma in lstTypeTurmasSemEspaçosUnique :
        myListOfCollegues= getAlunosOfSubjInSpecificClass(sem, subj, typeTurma, schoolYearObj)
        prices_json = json.dumps(myListOfCollegues, cls=DjangoJSONEncoder)
        type, turma= separateLettersNumb(typeTurma)
        if type not in list(dicTypeTurmasAlunos.keys()):
            dicTypeTurmasAlunos[type] = [[turma, prices_json]]
        else:
            dicTypeTurmasAlunos[type] = dicTypeTurmasAlunos[type] + [[turma, prices_json]]

    return dicTypeTurmasAlunos

def getAlunosOfSubjInSpecificClass(sem, subj, typeTurma, schoolYearObj):
    #ex: 1, AD, T11, 2018
    #obtem todos os alunos que pertencem a uma turma de uma determinada cadeira
    #retorna em json uma lista de listas, em q cada lista tem informaçao sobre um aluno
    
    suSubjs = list(SystemUserSubject.objects.filter(subject=subj, turmas__contains=typeTurma, anoLetivo=schoolYearObj, subjSemestre=sem))
    myListOfCollegues= []
    for suSubj in suSubjs:
        PI= PersonalInfo.objects.get(user=suSubj.user)
        listInfo= [suSubj.user.user.username, PI.name, suSubj.user.user.email]
        myListOfCollegues.append(listInfo)
    return myListOfCollegues

def uniqueElements(lst):
    newLst= []
    for e in lst:
        if e not in newLst :
            newLst.append(e)
    return newLst


def alterar_turmas_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/alterar_turmas.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def resposta_pedidos_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/resposta_pedidos_D.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def enviar_pedidos_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/enviar_pedido.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))

def presencas_consultar_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        return render(request, 'teacher/presenças_consulta.html', {})
    else: 
        return HttpResponseRedirect(reverse('login'))


def presencas_registar_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE) :
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == 'GET':
            suLessons = list(Lesson.objects.filter(professor=su))
            sem1SubjsStr= []
            sem2SubjsStr= []
            for lesson in suLessons:
                str= lesson.week_day + "," + lesson.hour + "," + lesson.subject.name + "," + lesson.type + "," + lesson.turma
                subj= lesson.subject
                CRsubjs= CourseSubject.objects.filter(subject=subj) 

                #se o sem da cadeira e igual independentemente do curso
                if is_semestres_all_same(CRsubjs) :
                    sem= CRsubjs[0].semester
                    if sem == 1:
                        sem1SubjsStr.append(str)
                    else:
                        sem2SubjsStr.append(str) 
                
                else:
                    sem1SubjsStr.append(str)
                    sem2SubjsStr.append(str)
            
            print(sem1SubjsStr)
            print(sem2SubjsStr)
            scheduleDict = {'1sem' : sem1SubjsStr, '2sem': sem2SubjsStr}
            return render(request, 'teacher/presenças_registo.html', {'scheduleDict':scheduleDict})
        
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)

            #prim pedido ajax
            if 'alunosEscolhidos' not in dadosJson :
                aulaEscolhidaInfo= dadosJson
                sem= aulaEscolhidaInfo['sem'][0]
                subjName= aulaEscolhidaInfo['cadeiraEscolhida']
                typeTurma= aulaEscolhidaInfo['turmaEscolhida']
                SubjObj= Subject.objects.get(name=subjName) 
                listAlunos= getAlunosOfSubjInSpecificClass(sem, SubjObj, typeTurma, schoolYearObj)
                return HttpResponse(json.dumps({"message": "success", "alunos": listAlunos}), content_type="application/json")
            
            #seg pedido ajax
            else:
                alunosEscolhidosInfo= dadosJson
                print(alunosEscolhidosInfo)
                alunosEscolhidos= alunosEscolhidosInfo['alunosEscolhidos']
                alunosNaoEscolhidos= alunosEscolhidosInfo['alunosNaoEscolhidos']
                subjName= alunosEscolhidosInfo['cadeiraEscolhida']
                typeTurma= alunosEscolhidosInfo['turmaEscolhida']
                lsttTypeTurma= separateLettersNumb(typeTurma)
                week_day= alunosEscolhidosInfo['week_day']
                SubjObj= Subject.objects.get(name=subjName) 
                lessonObj= Lesson.objects.get(subject=SubjObj, type=lsttTypeTurma[0], turma=lsttTypeTurma[1], week_day=week_day)
                date_str= dadosJson['date']
                dateFormat= datetime.strptime(date_str, "%d/%m/%Y").date()

                #remover dados que possam existir na bd naquela lesson naquele dia
                LessonSystemUser.objects.filter(lesson=lessonObj, date=dateFormat).delete()

                #tenho que criar novos dados, pq podem haver alunos novos nesta turma
                for alunoEsc in alunosEscolhidos:
                    userObj= User.objects.get(username= alunoEsc)
                    su = SystemUser.objects.get(user=userObj)
                    newLessonSU= LessonSystemUser(lesson=lessonObj, systemUser=su, presente=True, date=dateFormat)
                    newLessonSU.save()
                for alunoEsc in alunosNaoEscolhidos:
                    userObj= User.objects.get(username= alunoEsc)
                    su = SystemUser.objects.get(user=userObj)
                    newLessonSU= LessonSystemUser(lesson=lessonObj, systemUser=su, presente=False, date=dateFormat)
                    newLessonSU.save()
                return HttpResponse('')
          
            
    else: 
        return HttpResponseRedirect(reverse('login'))



# --------------------------------------------------------------------------------------------------------------------------------
#                                                        ADMIN
# --------------------------------------------------------------------------------------------------------------------------------
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


# --------------- teacher and student ---------------

def consult_details_post(request) :
    if request.method == 'POST':
            su = request_user(request)
            PIObject = PersonalInfo.objects.get(user=su)
            keyName = list(request.POST.keys())[0]
            print("." + keyName + ".")

            if keyName == "Nome: ":
                valor = request.POST.get(keyName)
                PIObject.name = valor

            if keyName == "Email Pessoal: ":
                valor = request.POST.get(keyName)

                try:
                    validate_email(valor)
                    PIObject.personal_email = valor

                except Exception:
                    messages.error(request, "O email que inseriu está errado!")


            if keyName == "Número Telefone: ":
                valor = request.POST.get(keyName)
                PIObject.phone_number = valor

            if keyName == "Morada: ":
                valor = request.POST.get(keyName)
                PIObject.address = valor

            if keyName == "Data de nascimento: ":
                valor = request.POST.get(keyName)
                PIObject.birth_date = valor

            if keyName == "Género: ":
                valor = request.POST.get(keyName)
                PIObject.gender = valor

            if keyName == "Nacionalidade: ":
                valor = request.POST.get(keyName)
                PIObject.nationality = valor

            if keyName == "Número de Identificação: ":
                valor = request.POST.get(keyName)
                PIObject.id_document = valor

            if keyName == "NIF/VAT: ":
                valor = request.POST.get(keyName)
                PIObject.vat_number = valor
            PIObject.save()


def horario_atual(request):
    u = request.user
    if u.is_authenticated:
        su = SystemUser.objects.get(user=u)
        roleName = su.role.role

        current_url = request.resolver_match.view_name

        if (roleName == "Admin") :
                return HttpResponseRedirect(reverse('login'))
        elif (roleName == "Professor") :
            if current_url != "horario_atual_t" : 
                return HttpResponseRedirect(reverse('horario_atual_t'))
            base_template = "teacher/base_t.html"
        else :
            if current_url != "horario_atual_s" : 
                return HttpResponseRedirect(reverse('horario_atual_s'))
            base_template = "student/base_s.html"


        schoolYearObj = SchoolYear.objects.get(begin=2018)
        sem1SubjsStr= []
        sem2SubjsStr= []
        sem1subjsName= []
        sem2subjsName= []


        #aluno
        if roleName == "Aluno" :
            suSubjs = SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj)        
            for suSubj in suSubjs :
                print(suSubj.turmas)
                lstTurmas= suSubj.turmas.split(" ")
                subj= suSubj.subject
                sem= suSubj.subjSemestre
                print(sem)
                #ex: lstTurmas-> ["T11","TP13","PL13"]
                lessons= []
                lstTurmasSemEspaços= [e for e in lstTurmas if e != ""]
                print(lstTurmasSemEspaços)
                for typeTurma in lstTurmasSemEspaços:
                    type, turma= separateLettersNumb(typeTurma)
                    turmaLessons= list(Lesson.objects.filter(subject=subj, type=type, turma=turma))
                    for lesson in turmaLessons:
                        str= lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
                        lessons.append(str)

                if sem == 1:
                    sem1SubjsStr= sem1SubjsStr + lessons
                    sem1subjsName.append(subj.name) 
                else:
                    sem2SubjsStr= sem2SubjsStr + lessons
                    sem2subjsName.append(subj.name) 


        else: #professor
            suLessons = list(Lesson.objects.filter(professor=su))
            for lesson in suLessons:
                str= lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
                subj= lesson.subject
                CRsubjs= CourseSubject.objects.filter(subject=subj) 

                #se o sem da cadeira e igual independentemente do curso
                if is_semestres_all_same(CRsubjs) :
                    sem= CRsubjs[0].semester
                    if sem == 1:
                        sem1SubjsStr.append(str)
                        if subj.name not in sem1subjsName:
                            sem1subjsName.append(subj.name) 
                    else:
                        sem2SubjsStr.append(str)
                        if subj.name not in sem2subjsName:
                            sem2subjsName.append(subj.name) 
                
                else:
                    sem1SubjsStr.append(str)
                    sem2SubjsStr.append(str)
                    if subj.name not in sem1subjsName:
                        sem1subjsName.append(subj.name) 
                    if subj.name not in sem2subjsName:
                        sem2subjsName.append(subj.name) 
            

        print(sem1SubjsStr)
        print(sem2SubjsStr)
        subjsName= {'1sem' : sem1subjsName, '2sem': sem2subjsName}
        scheduleDict = {'1sem' : sem1SubjsStr, '2sem': sem2SubjsStr}
        return render(request, 'horario.html', {'base_template':base_template, 'scheduleDict':scheduleDict, 'subjsName':subjsName})
    else: 
        return HttpResponseRedirect(reverse('login'))



def separateLettersNumb(string):
    #"TP13" fica ['TP', '13']
    return re.split('(\d+)',string)[:-1]


def is_semestres_all_same(courseSubjs):
    return all(crS.semester == courseSubjs[0].semester for crS in courseSubjs)










       

