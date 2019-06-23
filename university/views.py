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

#date django model, presenças
from datetime import datetime, timedelta

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
    def anoLetivo(d):
        if d >= datetime.strptime("20/9/2016", "%d/%m/%Y").date() and d <= datetime.strptime("31/5/2017", "%d/%m/%Y").date():
            return ("2016-2017")
        elif d >= datetime.strptime("18/9/2017", "%d/%m/%Y").date() and d <= datetime.strptime("30/5/2018", "%d/%m/%Y").date():
            return ("2017-2018")
        elif d >= datetime.strptime("17/9/2018", "%d/%m/%Y").date() and d <= datetime.strptime("31/5/2019", "%d/%m/%Y").date():
            return ("2018-2019")
        else:
            print("not found")

    if is_authenticated(request, university.models.STUDENT_ROLE) :
        su = request_user(request)
        presencas = list(LessonSystemUser.objects.filter(systemUser=su))
        presencasBySubject = {}
        subjects = []
        bySchoolYear = {}
        schoolYears = []
        for l in presencas:
            #anoLetivo(l.date)
            lessonName = l.lesson.get_subject_name()
            lessonNameWithoutWhitSpace = '_'.join(lessonName.split())
            lessonType = l.lesson.type
            if (lessonName, lessonNameWithoutWhitSpace) in presencasBySubject:
                if lessonType in presencasBySubject[(lessonName, lessonNameWithoutWhitSpace)]:
                    presencasBySubject[(lessonName, lessonNameWithoutWhitSpace)][lessonType].append((l.date, l.presente))
                else:
                    presencasBySubject[(lessonName, lessonNameWithoutWhitSpace)][lessonType] = [(l.date, l.presente)]
            else:
                presencasBySubject[(lessonName, lessonNameWithoutWhitSpace)] = {lessonType: [(l.date, l.presente)]}
            if (lessonName, lessonNameWithoutWhitSpace) not in subjects:
                subjects.append((lessonName, lessonNameWithoutWhitSpace))
            
            anoletivoStr = anoLetivo(l.date)
            if anoletivoStr not in schoolYears:
                schoolYears.append(anoletivoStr)
            
            bySchoolYear[anoletivoStr] = presencasBySubject

        return render(request, 'student/consult_presenças.html', {"bySchoolYear": bySchoolYear, "subjects": subjects, "schoolYears": schoolYears})
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
        if request.method == 'GET':
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

            NumberOfStudentsList=[]
            for sub in mySubjects:
                num = len(SystemUserSubject.objects.filter(anoLetivo = schoolYearObj, subject= sub).values_list("user__user").distinct())
                NumberOfStudentsList.append((sub, num))

            return render(request, 'teacher/home.html', {"suRegentes": regentes, "typesAndLessons" : my_dictionary, "NumStdBySub" : NumberOfStudentsList})
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))

            #horario cadeira, prim pedido ajax
            if 'nomeCadeira' in dadosJson :
                nomeCadeira= dadosJson['nomeCadeira']
                print(nomeCadeira)
                schedule= buildHorarioSubject(nomeCadeira)
                return HttpResponse(json.dumps({"message": "success", 'schedule':schedule}), content_type="application/json")
            
            #horario aluno, seg pedido ajax
            else: 
                alunoFc= dadosJson['aluno']
                print(alunoFc)
                u= User.objects.get(username= alunoFc)
                su= SystemUser.objects.get(user=u)
                schoolYearObj = SchoolYear.objects.get(begin=2018)
                subjsNameDict, scheduleDict= buildHorarioSystemUser("Aluno", su, schoolYearObj)
                return HttpResponse(json.dumps({"message": "success", 'scheduleDict':scheduleDict, 'subjsName':subjsNameDict}), content_type="application/json")


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
            schoolYearObj = SchoolYear.objects.get(begin=2018)
            dic1SemSubjs, dic2SemSubjs= getAllTypesturmasBySubjsGiveByTeacher(su, schoolYearObj)

            dic1SemSubjs = getAlunosOfTypesturmasInSubjs(1, dic1SemSubjs, schoolYearObj)
            dic2SemSubjs = getAlunosOfTypesturmasInSubjs(2, dic2SemSubjs, schoolYearObj)

            print(dic1SemSubjs)
            print(dic2SemSubjs)
            semestre= {"1": dic1SemSubjs, "2": dic2SemSubjs}

            #'scheduleDict':{}, 'subjsName':{}-> para nao dar erro no js
            return render(request, 'teacher/consult_turmas_D.html', {'subjsSem':semestre, 'scheduleDict':{}, 'subjsName':{}})
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))
            alunoFc= dadosJson['aluno']
            print(alunoFc)
            u= User.objects.get(username= alunoFc)
            su= SystemUser.objects.get(user=u)
            schoolYearObj = SchoolYear.objects.get(begin=2018)
            subjsNameDict, scheduleDict= buildHorarioSystemUser("Aluno", su, schoolYearObj)
            return HttpResponse(json.dumps({"message": "success", 'scheduleDict':scheduleDict, 'subjsName':subjsNameDict}), content_type="application/json")

    else: 
        return HttpResponseRedirect(reverse('login'))



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
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        dic1SemSubjs, dic2SemSubjs= getAllTypesturmasBySubjsGiveByTeacher(su, schoolYearObj)

        """
        2018/2019
            1º semestre: 17/09/2018(seg) a 19/12/2018(quarta)
            2º semestre: 18/02/2019(seg) a 31/05/2019(sex)
        """


        dataInicio= "17/09/2018"
        dataFinal= "19/12/2018"
        ano= "2018"
        joinFerias= allFeriasDate(ferias, ano)
        formatFeriados= convertFeriados(feriados, ano)
        joinFeriasAndFeriados= joinFerias + formatFeriados
        infoSemPresenças= [dataInicio, dataFinal, joinFeriasAndFeriados]
        dic1SemSubjs = getAlunosOfTypesturmasInSubjs(1, dic1SemSubjs, schoolYearObj, infoSemPresenças)

        dataInicio= "18/02/2019"
        dataFinal= "31/05/2019"
        ano= "2019"
        joinFerias= allFeriasDate(ferias, ano)
        formatFeriados= convertFeriados(feriados, ano)
        joinFeriasAndFeriados= joinFerias + formatFeriados
        infoSemPresenças= [dataInicio, dataFinal, joinFeriasAndFeriados]
        dic2SemSubjs = getAlunosOfTypesturmasInSubjs(2, dic2SemSubjs, schoolYearObj, infoSemPresenças)

        print(dic1SemSubjs)
        print(dic2SemSubjs)
        semestre= {"1": dic1SemSubjs, "2": dic2SemSubjs}

        return render(request, 'teacher/presenças_consulta.html', {"subjsSem": semestre})
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
                listAlunos= getAlunosOfClassInSpecificSubj(sem, SubjObj, typeTurma, schoolYearObj)
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



#------------------------------------------------ Funçoes auxiliares Teacher ------------------------------------------------
lstDiasDaSemana= ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
feriados = ['01/01', '19/04', '21/04', '25/04', '01/05', '10/06', '20/06', '15/08', '05/10', '01/11', '01/12', '08/12', '25/12'] #completo
ferias= [["04/03", "06/03"], #carnaval
         ["17/04", "23/04"]] #pascoa


def getAlunosOfTypesturmasInSubjs(sem, dicSemSubjs, schoolYearObj, infoSemPresenças=[]):
    #ex: 1, {<Subject: Subject object (1766)>: 'T12 T11', <Subject: Subject object (1767)>: 'T11'}, 2018
    print(dicSemSubjs)
    for subj in dicSemSubjs:
        print(dicSemSubjs[subj])
        dicSemSubjs[subj] = getAlunosOfClassesInSpecificSubj(sem, subj,  dicSemSubjs[subj], schoolYearObj, infoSemPresenças)
    return dicSemSubjs


def getAlunosOfClassesInSpecificSubj(sem, subj, string, schoolYearObj, infoSemPresenças=[]):
    #ex: 1, AD, " T11 TP12 T14 L15 T11", 2018
    #a string pode ter turmas repetitas por causa das lessons
    dicTypeTurmasAlunos= {}
    lstTypeTurmas= string.split(" ")
    lstTypeTurmasSemEspaços= [e for e in lstTypeTurmas if e != ""]
    print(lstTypeTurmasSemEspaços)
    lstTypeTurmasSemEspaçosUnique= uniqueElements(lstTypeTurmasSemEspaços)
    print(lstTypeTurmasSemEspaçosUnique)  #[T11, TP12, T14, L15]

    for typeTurma in lstTypeTurmasSemEspaçosUnique :
        myListOfCollegues= getAlunosOfClassInSpecificSubj(sem, subj, typeTurma, schoolYearObj, infoSemPresenças)
        prices_json = json.dumps(myListOfCollegues, cls=DjangoJSONEncoder)
        type, turma= separateLettersNumb(typeTurma)
        if type not in list(dicTypeTurmasAlunos.keys()):
            dicTypeTurmasAlunos[type] = [[turma, prices_json]]
        else:
            dicTypeTurmasAlunos[type] = dicTypeTurmasAlunos[type] + [[turma, prices_json]]

    return dicTypeTurmasAlunos

def getAlunosOfClassInSpecificSubj(sem, subj, typeTurma, schoolYearObj, infoSemPresenças=[]):
    #ex: 1, AD, T11, 2018
    #obtem todos os alunos que pertencem a uma turma de uma determinada cadeira
    #retorna em json uma lista de listas, em q cada lista tem informaçao sobre um aluno
    
    suSubjs = list(SystemUserSubject.objects.filter(subject=subj, turmas__contains=typeTurma, anoLetivo=schoolYearObj, subjSemestre=sem))
    print(infoSemPresenças)
    if infoSemPresenças :
        lstDates= getAllDatasByTypeturmaSubj2018_2019(subj, typeTurma, infoSemPresenças)
        print(lstDates) #ex: ['19/02/2019', '20/02/2019', ...]
    
    myListOfCollegues= []
    for suSubj in suSubjs:
        lstPresencasAluno= []
        for date in lstDates:
            pass
            #dataFormat=
            #lSU= LessonSystemUser.objects.filter(user)
        PI= PersonalInfo.objects.get(user=suSubj.user)
        if infoSemPresenças : #se nao for uma lista vazia
            presençasAluno= {}
            listInfo= [suSubj.user.user.username, PI.name, presençasAluno]
        else:
            listInfo= [suSubj.user.user.username, PI.name, suSubj.user.user.email]

        myListOfCollegues.append(listInfo)
    return myListOfCollegues

def uniqueElements(lst):
    #retorna os elementos unicos de uma lista
    newLst= []
    for e in lst:
        if e not in newLst :
            newLst.append(e)
    return newLst



def getAllDatasByTypeturmaSubj2018_2019(subj, typeTurma, infoSemPresenças):
    #ex: "T11", ["18/02/2019", "31/05/2019", joinFeriasAndFeriados]
    dataInicio, dataFinal, joinFeriasAndFeriados= infoSemPresenças
    type, turma= separateLettersNumb(typeTurma)
    turmaLessons= list(Lesson.objects.filter(subject=subj, type=type, turma=turma).values_list("week_day"))
    print(turmaLessons)
    diasDaSemanaStr= " ".join([tlesson[0] for tlesson in turmaLessons])
    print(diasDaSemanaStr)
    return getDatesBetween2Dates(dataInicio, dataFinal, joinFeriasAndFeriados, diasDaSemanaStr)


def getAllAlunosQueTemAulasComUmProf(systemUser, schoolYearObj):
    lstAlunos= []
    dic1SemSubjs, dic2SemSubjs= getAllTypesturmasBySubjsGiveByTeacher(systemUser, schoolYearObj)

    dic1SemSubjs = getAlunosOfTypesturmasInSubjs(1, dic1SemSubjs, schoolYearObj)
    dic2SemSubjs = getAlunosOfTypesturmasInSubjs(2, dic2SemSubjs, schoolYearObj)
    
    return lstAlunos


def getAllTypesturmasBySubjsGiveByTeacher(systemUser, schoolYearObj):
    suLessons = list(Lesson.objects.filter(professor=systemUser))
    
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

    print(dic1SemSubjs)
    print(dic2SemSubjs)
        
    return [dic1SemSubjs, dic2SemSubjs]
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
        subjsNameDict, scheduleDict= buildHorarioSystemUser(roleName, su, schoolYearObj)
        return render(request, 'horario.html', {'base_template':base_template, 'scheduleDict':scheduleDict, 'subjsName':subjsNameDict})
    else: 
        return HttpResponseRedirect(reverse('login'))



def separateLettersNumb(string):
    #"TP13" fica ['TP', '13']
    return re.split('(\d+)',string)[:-1]


def is_semestres_all_same(courseSubjs):
    return all(crS.semester == courseSubjs[0].semester for crS in courseSubjs)


def buildHorarioSystemUser(roleName, systemUser, schoolYearObj):
    sem1SubjsStr= []
    sem2SubjsStr= []
    sem1subjsName= []
    sem2subjsName= []

    #aluno
    if roleName == "Aluno" :
        #todas as cadeiras que o aluno esta inscrito neste ano
        suSubjs = SystemUserSubject.objects.filter(user=systemUser, anoLetivo=schoolYearObj)        
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

            #todas as turmas em q o aluno esta inscrito numa cadeira
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

    #professor
    else: 
        suLessons = list(Lesson.objects.filter(professor=systemUser))
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
    subjsNameDict= {'1sem' : sem1subjsName, '2sem': sem2subjsName}
    scheduleDict = {'1sem' : sem1SubjsStr, '2sem': sem2SubjsStr}
    return [subjsNameDict, scheduleDict]



def buildHorarioSubject(nameSubj):
    subjectObj= Subject.objects.get(name= nameSubj)
    lessons= list(Lesson.objects.filter(subject=subjectObj))
    lstLessonsStr= []

    for lesson in lessons:
        str= lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
        lstLessonsStr.append(str)
    
    return lstLessonsStr





#------------------------------------------------ Funçoes auxiliares Datas ------------------------------------------------

def getDatesBetween2Dates(dataInicio, dataFinal, lazyDays=None, diasDaSemana=lstDiasDaSemana):
  """
  devolve todas as datas que calham em dias de semana especificos
  lazyDays != none, retira as datas q sejam feriados ou no periodo de mini ferias
  diasDaSemana -> os dias da semana que quero as datas, pode ser uma lista ou uma string(ex: "TER QUI")

  recebe: ex: 17/04/2017, 23/04/2017, None, ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
  retorna: ex: ['17/04/2017', '18/04/2017', ... , '22/04/2017', '23/04/2017']

  recebe: ex: 18/09/2017, 21/12/2017, ['04/03/2017', '05/03/2017', ...], "QUARTA" (ou 'QUA')
  retorna: ex: ['20/09/2017', '27/09/2017', '04/10/2017', ...,  '20/12/2017']
  """
  start_date  = datetime.strptime(dataInicio, '%d/%m/%Y')
  end_date    = datetime.strptime(dataFinal, '%d/%m/%Y')

  if lazyDays == None:
    lstDates= [] 
  else:
    lstWorkDates= []

  for i in range(-1, (end_date - start_date).days, 1):
    nextDate= start_date + timedelta(days=i+1)
    diaDaSemana= lstDiasDaSemana[nextDate.weekday()]
    if diaDaSemana in diasDaSemana:
      date_str= nextDate.date().strftime('%d/%m/%Y')
      #print(date_str)
      if lazyDays == None:
        lstDates.append(date_str)
      else:
        if date_str not in lazyDays: 
          lstWorkDates.append(date_str)

  
  if lazyDays == None:
    return lstDates
  else: 
    return lstWorkDates


def convertFerias(ferias, ano):
  #recebe ex: ferias= [["04/03", "06/03"], ["17/04", "23/04"]], ano=2018
  #retorna ex: [['04/03/201*', '06/03/201*'], ['17/04/201*', '23/04/201*']]
  return list(map(lambda lst: list(map(lambda dm: dm + "/" + ano, lst)), ferias))

def convertFeriados(feriados, ano):
  #recebe ex: feriados = ['01/01', '19/04', ... ], ano=2018
  #retorna ex: feriados = ['01/01/201*', '19/04/201*', '21/04/201*', ...]
  return list(map(lambda dm: dm + "/" + ano, feriados))


def allFeriasDate(ferias, ano):
  #recebe ex: ferias= [["04/03", "06/03"], ["17/04", "23/04"]], ano=2018
  #retorna ex: ['04/03/2018', '05/03/2018', '06/03/2018', '17/04/2018', '18/04/2018', ... , '23/04/2018']
  newFerias= convertFerias(ferias, ano)
  newFerias_str= []
  for f in newFerias:
    dataInicio, dataFinal= f
    newFerias_str = newFerias_str + getDatesBetween2Dates(dataInicio, dataFinal)
  return newFerias_str
       

