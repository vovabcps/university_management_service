from django.core.files.base import ContentFile
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

# convert to json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout

# models
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import *
import university.models

# app_list
from django.contrib import admin

# connection db
from django.db import connection
from django.core.files.storage import FileSystemStorage, default_storage

import sys
import re
from itertools import groupby
from django.db.models import Q
import operator
from functools import reduce
import copy

# password change
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

# consult details
from django.core.validators import validate_email

# date django model, presenças
from datetime import datetime, timedelta


# --------------------- all in common -----------------------

def password_change(request):
    u = request.user
    if u.is_authenticated:
        su = SystemUser.objects.get(user=u)
        roleName = su.role.role

        current_url = request.resolver_match.view_name

        if (roleName == "Admin"):
            if current_url != "password_change_a":
                return HttpResponseRedirect(reverse('password_change_a'))
            base_template = "admin/base_site.html"
        elif (roleName == "Professor"):
            if current_url != "password_change_t":
                return HttpResponseRedirect(reverse('password_change_t'))
            base_template = "teacher/base_t.html"
        else:
            if current_url != "password_change_s":
                return HttpResponseRedirect(reverse('password_change_s'))
            base_template = "student/base_s.html"

        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                # return redirect('password_change_a') #se correr bem
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'password_alt.html',
                      {'form': form, 'roleName': roleName, 'base_template': base_template})  # se correr mal
    else:
        return HttpResponseRedirect(reverse('login'))


def is_authenticated(request, role_name):
    u = request.user
    if u.is_authenticated:
        su = SystemUser.objects.get(user=u)
        role = su.role
        return role.is_a(role_name)
    return False


# --------------- login ---------------
@csrf_exempt
def login_page(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect_to_user_home(request)
        return render(request, 'login.html', {})
    elif request.method == "POST":
        return login_user(request)


def redirect_to_user_home(request):
    su = request_user(request)
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
    # print(username, password)
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
    if is_authenticated(request, university.models.STUDENT_ROLE):

        if request.method == 'GET':
            su = request_user(request)
            schoolYearObj = SchoolYear.objects.get(begin=2018)
            inscrito = list(SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj))
            # print(inscrito)

            suCourse = SystemUserCourse.objects.get(user=su).course

            regentes = []
            for sub in inscrito:
                if PersonalInfo.objects.filter(user=sub.subject.regente).first() not in regentes:
                    regentes.append(PersonalInfo.objects.filter(user=sub.subject.regente).first())

            listofSubs = []
            for line in inscrito:
                listofSubs.append(line.subject)

            ohlord = (list(Lesson.objects.filter(subject__in=listofSubs).values("subject__name", "professor__user")))

            from itertools import groupby

            tempList = []
            myLastList = []

            for sub_name, g in groupby(ohlord, lambda a: a["subject__name"]):
                print(sub_name)

                listofTeachers = []
                a = copy.deepcopy(g)
                for d in a:
                    if d["professor__user"] not in listofTeachers:
                        listofTeachers.append(d["professor__user"])
                        tempList.append(d["professor__user"])
                myLastList.append((sub_name, listofTeachers))
                print(listofTeachers)
            print(tempList)

            finallyDone = list(PersonalInfo.objects.filter(user__user__in=tempList).values("user__user", "name"))

            TrueFinalList = []
            for tuple in myLastList:
                sub = tuple[0]
                teacher_string = ""
                for line in finallyDone:
                    if line["user__user"] in tuple[1]:
                        teacher_string += line["name"] + ", "
                TrueFinalList.append((sub, teacher_string[:-2]))

            return render(request, 'student/home.html',
                          {"suAllSubjects": inscrito, "suRegentes": regentes, "myTeachersBoyy": TrueFinalList})

        else:
            dadosJson = json.loads(request.body.decode("utf-8"))

            # horario cadeira, prim pedido ajax
            nomeCadeira = dadosJson['nomeCadeira']
            print(nomeCadeira)
            schedule = buildHorarioSubject(nomeCadeira)
            return HttpResponse(json.dumps({"message": "success", 'schedule': schedule}),
                                content_type="application/json")
    else:
        return HttpResponseRedirect(reverse('login'))


def inscricoes_subject_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        inscrito = SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj).first()

        # verificar se o aluno ja esta incrito em cadeiras de um curso
        if not inscrito:
            # cadeiras que ele nao se pode inscrever pq ja foi aprovado
            SystemUserSubjectObjs = SystemUserSubject.objects.filter(user=su,
                                                                     state=1)  # qd se esta a increver nao a pending(ou foi aprovado ou reprovou)
            subjsAprov = []
            for SystemUSubjectObj in SystemUserSubjectObjs:
                subjsAprov.append(SystemUSubjectObj.subject)
            print(len(subjsAprov))

            # curso do aluno
            suCourse = SystemUserCourse.objects.get(user=su)

            anosCreditos = suCourse.course.credits_numberByYear  # 1:60|2:60|3:60
            lstAnoCred = anosCreditos.split("|")
            dicAnoSubjs = {}

            for anoCred in lstAnoCred:
                ano, cred = anoCred.split(":")
                credFeitosAno = 0
                credFeitosSubjsObrig = 0
                credTotalTroncoComum = 0

                # as cadeiras obrigatorias q ele vai ter nesse ano
                courseObrig_subjs = CourseSubject.objects.filter(course=suCourse.course, year=int(ano)).order_by(
                    "semester")

                # as cadeiras obrigatorias que ele ainda n foi aprovado
                courseObrig_subjsPorFazer = []
                for courseObrig_subj in courseObrig_subjs:
                    credTotalTroncoComum += courseObrig_subj.subject.credits_number
                    if courseObrig_subj.subject not in subjsAprov:
                        courseObrig_subjsPorFazer.append(courseObrig_subj)
                    else:  # se ele ja fez a cadeira
                        print(courseObrig_subj.subject.name)
                        credFeitosSubjsObrig += courseObrig_subj.subject.credits_number

                subjsObrig = [credTotalTroncoComum, credFeitosSubjsObrig, courseObrig_subjsPorFazer]
                credFeitosAno += credFeitosSubjsObrig

                # quais sao os mini cursos q o aluno vai ter naquele ano
                miniCs = Course_MiniCourse.objects.filter(course=suCourse.course, year=int(ano))

                # as cadeiras dos mini cursos daquele ano
                miniCursosOthersSubjs = []  # lista de listas, todos os mini cursos exepto minors
                minor = []
                for miniC in miniCs:
                    credNecessarios = miniC.credits_number
                    credFeitos = 0
                    if miniC.miniCourse.grau != "Minor":
                        if len(miniC.semestres) == 1:
                            miniCsubjs = CourseSubject.objects.filter(course=miniC.miniCourse, year=ano,
                                                                      semester=int(miniC.semestres))
                        else:
                            miniCsubjs = CourseSubject.objects.filter(course=miniC.miniCourse, year=ano).order_by(
                                "semester")

                        # remover as cadeiras em q o aluno ja foi aprovado
                        miniCsubjsPorFazer = []
                        for miniCsubj in miniCsubjs:
                            if miniCsubj.subject not in subjsAprov:
                                miniCsubjsPorFazer.append(miniCsubj)
                            else:
                                print(miniCsubj.subject.name)
                                credFeitos += miniCsubj.subject.credits_number

                        if credFeitos < credNecessarios:  # se ele ainda tem cred para fazer do mini curso
                            miniCursosOthersSubjs.append([miniC, credFeitos, miniCsubjsPorFazer])
                        else:  # se ele ja completou o minicurso
                            miniCursosOthersSubjs.append([miniC, credFeitos, []])

                    # se naquele curso e naquele ano houver minor e ele foi admitdo
                    elif miniC.miniCourse.name == suCourse.minor:
                        miniCsubjs = CourseSubject.objects.filter(course=miniC.miniCourse, year=ano).order_by(
                            "semester")
                        minor = [[miniC, credFeitos, miniCsubjs]]

                    credFeitosAno += credFeitos

                dicMinorsAndOthers = {'others': miniCursosOthersSubjs, 'minor': minor}
                course_subjs = {'courseObrig_subjs': subjsObrig, 'miniCs_subjs': dicMinorsAndOthers}

                # se ele ainda tiver cadeiras para fazer neste ano:
                # if len(minor) != 0 or len(miniCursosOthersSubjs) != 0 or len(courseObrig_subjsPorFazer) != 0 :
                dicAnoSubjs[ano + "º ano"] = {'ceditos': [credFeitosAno, cred], 'course_subjs': course_subjs}

            return render(request, 'student/inscricoes_subject.html',
                          {'suCourse': suCourse, 'dicAnoSubjs': dicAnoSubjs})
        else:
            messages.error(request, "Ja esta inscrito/a nas cadeiras do seu curso deste ano!")
            return HttpResponseRedirect(reverse('home_s'))
    else:
        return HttpResponseRedirect(reverse('login'))


def choose_lessons_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        if request.method == 'POST':
            valid = True
            print(request.POST)  # so vai buscar as q foram escolhidas!

            dic = dict(request.POST)
            dic.pop('csrfmiddlewaretoken')
            print(dic)

            if len(dic) == 0:  # se nao escolher nenhuma cadeira
                valid = False
                messages.error(request, "Escolha pelo menos uma cadeira!!")

            subjsNameEscolhidas = []
            subjsEscolhidas = []
            credTotaisEscolhidos = 0
            print(list(dic.keys()))
            for anoCourseCredTotalCredFeitos in dic:
                ano, course, credTotais, credFeitos = anoCourseCredTotalCredFeitos.split("|")
                credTotaisSubj = 0
                for subjSemCred in dic[anoCourseCredTotalCredFeitos]:
                    # print(anoCourseCredTotalCredFeitos + ": " + subjSemCred)
                    subjsEscolhidas.append(subjSemCred)
                    subj, sem, cred = subjSemCred.split("|")
                    subjsNameEscolhidas.append(subj)
                    credTotaisEscolhidos += int(cred)
                    credTotaisSubj += int(cred)

                if credTotaisSubj + int(credFeitos) > int(credTotais):
                    valid = False
                    messages.error(request,
                                   "Não pode ultrapassar os " + credTotais + " cred. de " + course + " do " + ano)

            if credTotaisEscolhidos > 72:
                valid = False
                messages.error(request, "Não pode ultrapassar os 72 creditos!!!")

            if escolheu_a_msm_subj_mais_q_uma_vez(subjsNameEscolhidas):
                valid = False
                messages.error(request, "So pode escolher 1 vez a mesma cadeira!!")

            if valid:  # se tiver tudo bem
                dic1SemSubjs = {}
                dic2SemSubjs = {}

                for subjNameSem in subjsEscolhidas:
                    dicTypeTurmaLessons = {}
                    # print(subjNameSem)
                    subjName, subjSem, subCred = subjNameSem.split("|")
                    # print(subjName, subjSem)
                    SubjObj = Subject.objects.get(name=subjName)
                    lessons = Lesson.objects.filter(subject=SubjObj).order_by("type").order_by("turma")
                    for l in lessons:
                        detalhes = l.week_day + "," + l.hour + "," + l.duration + "," + l.subject.name + "," + l.type + "," + l.room.room_number + "|"
                        if l.type in dicTypeTurmaLessons:
                            novaTurma = True
                            for [turma, lstLessons] in dicTypeTurmaLessons[l.type]:
                                if turma == l.turma:
                                    # print(lstLessons)
                                    oldList = [[t, ls] for [t, ls] in dicTypeTurmaLessons[l.type] if t != l.turma]
                                    dicTypeTurmaLessons[l.type] = oldList + [[l.turma, lstLessons + detalhes]]
                                    novaTurma = False
                                    break
                            if novaTurma:
                                dicTypeTurmaLessons[l.type] = dicTypeTurmaLessons[l.type] + [[l.turma, detalhes]]

                        else:
                            dicTypeTurmaLessons[l.type] = [[l.turma, detalhes]]  # nao por tuplos pq eles sao imutaveis
                    if subjSem == "1":
                        dic1SemSubjs[SubjObj] = dicTypeTurmaLessons
                    else:
                        dic2SemSubjs[SubjObj] = dicTypeTurmaLessons

                semestre = {"1": dic1SemSubjs, "2": dic2SemSubjs}

                return render(request, 'student/choose_lessons.html', {'subjsSem': semestre})
            else:
                return HttpResponseRedirect(reverse('inscricoes_subject_s'))

        else:
            return HttpResponseRedirect(reverse('inscricoes_subject_s'))
    else:
        return HttpResponseRedirect(reverse('login'))


def escolheu_a_msm_subj_mais_q_uma_vez(lst):
    return len(lst) != len(set(lst))


def inscricoes_confirmacao_s(request):
    # verifica os dados da pag choose_lessons
    if is_authenticated(request, university.models.STUDENT_ROLE):
        if request.method == 'POST':
            subjsNameSemestre = json.loads(request.body.decode("utf-8"))
            # print(subjsNameSemestre)
            semestre1 = subjsNameSemestre['1semLessons']
            semestre2 = subjsNameSemestre['2semLessons']
            totalLessons = subjsNameSemestre['totalLessons']
            print(semestre1)
            # ex: Produção de Documentos Técnicos|14|TP||Produção de Documentos Técnicos|16|PL||Programação I (LTI)|17|PL||Programação I (LTI)|14|TP||
            # Elementos de Matemática II|21|TP||Introdução às Probabilidades e Estatística|21|T||Introdução às Probabilidades e Estatística|23|TP||
            print(semestre2)
            print(totalLessons)
            subjLessonsSem1 = semestre1.split("||")[:-1]
            subjLessonsSem2 = semestre2.split("||")[:-1]

            if (len(subjLessonsSem1) + len(subjLessonsSem2)) != totalLessons:
                valid = False
            else:
                valid = True

            if valid:  # se tiver tudo bem
                sysUser = request_user(request)
                subjLessons = [subjLessonsSem1, subjLessonsSem2]
                schoolYearObj = SchoolYear.objects.get(begin=2018)
                # inscrever nas cadeiras
                subjNameBefor = None
                sem = 1
                for subjLessonsSem in subjLessons:
                    for subjLess in subjLessonsSem:
                        subjNameLesson = subjLess.split("|")
                        subjName, turma, type = subjNameLesson
                        if subjName != subjNameBefor:
                            SubjObj = Subject.objects.get(name=subjName)
                            newSysUSubj = SystemUserSubject(user=sysUser, subject=SubjObj, state=0, subjSemestre=sem,
                                                            anoLetivo=schoolYearObj)
                            newSysUSubj.save()
                            turmas = " "
                            subjNameBefor = subjName

                        turmas = turmas + type + turma + " "
                        newSysUSubj.turmas = turmas
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
    if is_authenticated(request, university.models.STUDENT_ROLE):

        class FearAllWhoCodeThis:

            def __init__(self, tab_name, sub_name, classes_students):
                self.id = "#" + tab_name
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

            myListOfTuples = []
            for typeTurma in lstTurmasSemEspaços:
                # subjSemestre = sem

                myList = list(
                    SystemUserSubject.objects.filter(subject=subj, turmas__contains=typeTurma, anoLetivo=schoolYearObj,
                                                     subjSemestre=sem))
                print(typeTurma)
                print(subj.name)

                myListOfCollegues = []
                for line in myList:
                    myListOfCollegues.append(PersonalInfo.objects.get(user=line.user))
                print(myListOfCollegues)
                myListOfTuples.append((typeTurma, myListOfCollegues))

            finalList.append(FearAllWhoCodeThis("tab" + str(i), subj.name, myListOfTuples))
            i += 1

        return render(request, 'student/consult_contacts.html', {"finalList": finalList})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_details_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        consult_details_post(request)
        return render(request, 'student/consult_details.html', {})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_subjects_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        inscrito = list(SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj))
        # print(inscrito)

        suCourse = SystemUserCourse.objects.get(user=su).course
        allMyCourseSubj = list(CourseSubject.objects.filter(course=suCourse))

        miniCs = Course_MiniCourse.objects.filter(course=suCourse)
        # print(miniCs)

        nameBefore = []
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

        listofSubs = []
        for line in inscrito:
            listofSubs.append(line.subject)

        ohlord = (list(Lesson.objects.filter(subject__in=listofSubs).values("subject__name", "professor__user")))

        from itertools import groupby

        tempList = []
        myLastList = []

        for sub_name, g in groupby(ohlord, lambda a: a["subject__name"]):
            print(sub_name)

            listofTeachers = []
            a = copy.deepcopy(g)
            for d in a:
                if d["professor__user"] not in listofTeachers:
                    listofTeachers.append(d["professor__user"])
                    tempList.append(d["professor__user"])
            myLastList.append((sub_name, listofTeachers))
            print(listofTeachers)
        print(tempList)

        finallyDone = list(PersonalInfo.objects.filter(user__user__in=tempList).values("user__user", "name"))

        TrueFinalList = []
        for tuple in myLastList:
            sub = tuple[0]
            teacher_string = ""
            for line in finallyDone:
                if line["user__user"] in tuple[1]:
                    teacher_string += line["name"] + ", "
            TrueFinalList.append((sub, teacher_string[:-2]))

        return render(request, 'student/consult_subjects.html',
                      {"suAllSubjects": inscrito, "suRegentes": regentes, "allMyCourseSubj": allMyCourseSubj,
                       "myTeachersBoyy": TrueFinalList})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_presencas_s(request):
    def anoLetivo(d):
        if d >= datetime.strptime("20/9/2016", "%d/%m/%Y").date() and d <= datetime.strptime("31/5/2017",
                                                                                             "%d/%m/%Y").date():
            return ("2016-2017")
        elif d >= datetime.strptime("18/9/2017", "%d/%m/%Y").date() and d <= datetime.strptime("30/5/2018",
                                                                                               "%d/%m/%Y").date():
            return ("2017-2018")
        elif d >= datetime.strptime("17/9/2018", "%d/%m/%Y").date() and d <= datetime.strptime("31/5/2019",
                                                                                               "%d/%m/%Y").date():
            return ("2018-2019")
        else:
            print("not found")

    if is_authenticated(request, university.models.STUDENT_ROLE):
        su = request_user(request)
        presencas = list(LessonSystemUser.objects.filter(systemUser=su))

        bySchoolYear = {}
        schoolYears = []
        for l in presencas:
            lessonName = l.lesson.get_subject_name()
            lessonNameWithoutWhitespace = '_'.join(lessonName.split("(")[0].split())
            tupleLessonName = (lessonName, lessonNameWithoutWhitespace)
            lessonType = l.lesson.type
            anoletivo = anoLetivo(l.date)

            if anoletivo not in schoolYears:
                schoolYears.append(anoletivo)

            if anoletivo not in bySchoolYear:
                bySchoolYear[anoletivo] = {}

            if tupleLessonName not in bySchoolYear[anoletivo]:
                bySchoolYear[anoletivo][tupleLessonName] = {}

            if lessonType not in bySchoolYear[anoletivo][tupleLessonName]:
                if l.presente == True:
                    bySchoolYear[anoletivo][tupleLessonName][lessonType] = [[1, 100], [(l.date, l.presente)]]
                else:
                    bySchoolYear[anoletivo][tupleLessonName][lessonType] = [[0, 0], [(l.date, l.presente)]]
            else:
                bySchoolYear[anoletivo][tupleLessonName][lessonType][1].append((l.date, l.presente))
                classesTotal = len(bySchoolYear[anoletivo][tupleLessonName][lessonType][1])
                if l.presente == True:
                    bySchoolYear[anoletivo][tupleLessonName][lessonType][0][0] += 1

                classes = bySchoolYear[anoletivo][tupleLessonName][lessonType][0][0]
                percentage = (float(classes) / float(classesTotal)) * 100
                bySchoolYear[anoletivo][tupleLessonName][lessonType][0][1] = percentage

        schoolYears.sort()
        return render(request, 'student/consult_presenças.html',
                      {"bySchoolYear": bySchoolYear, "schoolYears": schoolYears})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_university_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        listaFacs = list(Faculdade.objects.all())
        return render(request, 'student/consult_university.html', {"listaFaculdades": listaFacs})
    else:
        return HttpResponseRedirect(reverse('login'))


def request_change_lesson_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == "GET":
            #### Turmas atuais
            class RequestChangeLesson:

                def __init__(self, tab_name, sub_name, sub_reg, classes_students, classes_list_turmas):
                    self.id = "#" + tab_name
                    self.idNoHashTag = tab_name
                    self.idNoHashTagRadio = "radio" + tab_name
                    self.subjectName = sub_name
                    self.subjectRegente = sub_reg
                    self.classes = classes_students
                    self.classest = classes_list_turmas

            finalList = []

            suSubjs = SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj)

            i = 1
            for suSubj in suSubjs:
                subj = suSubj.subject
                sem = suSubj.subjSemestre
                SUregente = subj.regente
                piObj = PersonalInfo.objects.get(user=SUregente)
                regenteName = piObj.name
                lstTurmas = suSubj.turmas.split(" ")
                # ex: lstTurmas-> ["T11","TP13","PL13"]
                lstTurmasSemEspaços = [e for e in lstTurmas if e != ""]

                # Turmas todas
                discTurmas = Lesson.objects.values_list('subject__name', 'type', 'turma', 'week_day', 'hour',
                                                        'room__room_number').filter(subject=subj)

                tTurmaComp = list()

                for discTurma in discTurmas:
                    if discTurma[1] + str(discTurma[2]) not in lstTurmasSemEspaços:

                        tSubj = discTurma[0]
                        tType = discTurma[1]
                        tTurma = discTurma[2]

                        a = tType + str(tTurma)

                        if a not in tTurmaComp:
                            tTurmaComp.append(a)

                finalList.append(
                    RequestChangeLesson("tab" + str(i), subj.name, regenteName, lstTurmasSemEspaços, tTurmaComp))
                i += 1

            return render(request, 'student/request_change_lesson.html', {"finalList": finalList})
        elif request.method == "POST":

            # i had no choice sry
            #### Turmas atuais
            class RequestChangeLesson:

                def __init__(self, sub_name, classes_students, classes_list_turmas):
                    self.subjectName = sub_name
                    self.classes = classes_students
                    self.classest = classes_list_turmas

            finalList = []

            suSubjs = SystemUserSubject.objects.filter(user=su, anoLetivo=schoolYearObj)

            for suSubj in suSubjs:
                subj = suSubj.subject

                lstTurmas = suSubj.turmas.split(" ")
                # ex: lstTurmas-> ["T11","TP13","PL13"]
                lstTurmasSemEspaços = [e for e in lstTurmas if e != ""]

                # Turmas todas
                discTurmas = Lesson.objects.values_list('subject__name', 'type', 'turma', 'week_day', 'hour',
                                                        'room__room_number').filter(subject=subj)

                tTurmaComp = list()

                for discTurma in discTurmas:
                    if discTurma[1] + str(discTurma[2]) not in lstTurmasSemEspaços:
                        tType = discTurma[1]
                        tTurma = discTurma[2]

                        a = tType + str(tTurma)
                        if a not in tTurmaComp:
                            tTurmaComp.append(a)

                finalList.append(RequestChangeLesson(subj.name, lstTurmasSemEspaços, tTurmaComp))

            print(finalList)
            dadosJson = json.loads(request.body.decode("utf-8"))

            inf = dadosJson['new_info']
            my_pretty_info = inf.split("|")

            req_subject = my_pretty_info[0]
            old_class = my_pretty_info[1]
            new_class = my_pretty_info[2]

            def validate_input(re_subject, old_class, new_class, finalList):

                for obj in finalList:
                    if obj.subjectName == re_subject and old_class in obj.classes and new_class in obj.classest:
                        if separateLettersNumb(old_class)[0] == separateLettersNumb(new_class)[0]:
                            pedidosSent = list(
                                SystemUserMensagens.objects.filter(remetente=su, subject__name=re_subject))
                            for pedido in pedidosSent:
                                if pedido.is_accepted != True and pedido.is_accepted != False and pedido.turmaInicial == old_class:
                                    return False

                            pedidosRecieved = list(
                                SystemUserMensagens.objects.filter(destinatario=su, subject__name=re_subject))
                            for pedidoR in pedidosRecieved:
                                if pedidoR.is_accepted != True and pedidoR.is_accepted != False and pedidoR.turmaInicial == old_class:
                                    return False

                            return True

                        return False

                return False

            if validate_input(req_subject, old_class, new_class, finalList):
                sub = Subject.objects.get(name=req_subject)

                newSysUserMens = SystemUserMensagens(remetente=su, destinatario=sub.regente, subject=sub,
                                                     turmaInicial=old_class, turmaFinal=new_class)
                newSysUserMens.save()

                return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
            else:

                return HttpResponse(json.dumps({"message": "failure"}), content_type="application/json")

    else:
        return HttpResponseRedirect(reverse('login'))


def estado_pedidos_s(request):
    if is_authenticated(request, university.models.STUDENT_ROLE):
        if request.method == "GET":
            su = request_user(request)
            pedidos = list(SystemUserMensagens.objects.filter(destinatario=su))

            listPedidos = []
            historicoPedidos = []
            for p in pedidos:
                teacher = PersonalInfo.objects.get(user=p.remetente)
                subj = p.subject
                startClass = p.turmaInicial
                finalClass = p.turmaFinal
                status = p.is_accepted
                if status == True or status == False:
                    historicoPedidos.append((teacher, subj, startClass, finalClass, status))
                else:
                    listPedidos.append((teacher, subj, startClass, finalClass, status))

            pedidosSent = list(SystemUserMensagens.objects.filter(remetente=su))
            pedidosS = []
            for ap in pedidosSent:
                student = PersonalInfo.objects.get(user=ap.destinatario)
                subj = ap.subject
                startClass = ap.turmaInicial
                finalClass = ap.turmaFinal
                status = ap.is_accepted
                if status != True and status != False:
                    status = "Enviado"
                pedidosS.append((student, subj, startClass, finalClass, status))

            return render(request, 'student/estado_pedidos.html',
                          {"listPedidos": listPedidos, "historicoPedidos": historicoPedidos, "pedidosS": pedidosS})

        elif request.method == "POST":
            dadosJson = json.loads(request.body.decode("utf-8"))

            inf = dadosJson['info']
            info = inf.split("|")  # [{{subj}}|{{teacher}}|{{start}}|{{final}}|True]

            teacherSystem = PersonalInfo.objects.get(name=info[1])
            subjSystem = Subject.objects.get(name=info[0])
            initial = info[2]
            final = info[3]

            update = SystemUserMensagens.objects.get(subject=subjSystem, remetente=teacherSystem.user,
                                                     turmaInicial=initial, turmaFinal=final)

            if info[4] == "True":
                update.is_accepted = True

                su = request_user(request)
                pedidos = SystemUserSubject.objects.get(user=su, subject=subjSystem)
                turmas = pedidos.turmas.split()
                for t in turmas:
                    if t == initial:
                        turmas.pop(turmas.index(t))
                        turmas.append(final)
                        break
                turmasStr = " ".join(turmas)
                pedidos.turmas = turmasStr
                pedidos.save()

            elif info[4] == "False":
                update.is_accepted = False

            update.save()

            return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
    else:
        return HttpResponseRedirect(reverse('login'))


# --------------------------------------------------------------------------------------------------------------------------------
#                                                        teacher
# --------------------------------------------------------------------------------------------------------------------------------

def home_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        if request.method == 'GET':
            su = request_user(request)
            schoolYearObj = SchoolYear.objects.get(begin=2018)
            inscrito = list(Lesson.objects.filter(professor=su))
            # print(inscrito)
            mySubjects = []
            mySubjectsName = []
            my_dictionary = {}  # key:cadeira, value: turmas em q ele da aulas dessa cadeira

            for subj in inscrito:
                if subj.subject not in list(my_dictionary.keys()):
                    my_dictionary[subj.subject] = ""
                    mySubjects.append(subj.subject)
                    mySubjectsName.append(subj.subject.name)

                if (subj.type + subj.turma) not in my_dictionary[subj.subject]:
                    my_dictionary[subj.subject] = my_dictionary[subj.subject] + subj.type + subj.turma + " "

            for subj in mySubjects:
                my_dictionary[subj] = my_dictionary[subj][:-1]

            regentes = []
            for sub in inscrito:
                if PersonalInfo.objects.filter(user=sub.subject.regente).first() not in regentes:
                    regentes.append(PersonalInfo.objects.filter(user=sub.subject.regente).first())

            listofSubs = []
            for line in inscrito:
                listofSubs.append(line.subject)

            ohlord = (list(Lesson.objects.filter(subject__in=listofSubs).values("subject__name", "professor__user")))

            from itertools import groupby

            tempList = []
            myLastList = []

            for sub_name, g in groupby(ohlord, lambda a: a["subject__name"]):
                print(sub_name)

                listofTeachers = []
                a = copy.deepcopy(g)
                for d in a:
                    if d["professor__user"] not in listofTeachers:
                        listofTeachers.append(d["professor__user"])
                        tempList.append(d["professor__user"])
                myLastList.append((sub_name, listofTeachers))
                print(listofTeachers)
            print(tempList)

            finallyDone = list(PersonalInfo.objects.filter(user__user__in=tempList).values("user__user", "name"))

            TrueFinalList = []
            for tuple in myLastList:
                sub = tuple[0]
                teacher_string = ""
                for line in finallyDone:
                    if line["user__user"] in tuple[1]:
                        teacher_string += line["name"] + ", "
                TrueFinalList.append((sub, teacher_string[:-2]))

            NumberOfStudentsList = []
            for sub in mySubjects:
                num = len(SystemUserSubject.objects.filter(anoLetivo=schoolYearObj, subject=sub).values_list(
                    "user__user").distinct())
                NumberOfStudentsList.append((sub, num))

            # -------------- Sobreposicoes --------------
            dicAlunosSobreposicoes = {}
            # print(mySubjectsName)
            lstAlunos = getAllAlunosQueTemAulasComUmProf(su, schoolYearObj)

            if lstAlunos:  # se tiver alunos
                dicAlunosScheduleDic = buildHorarioLstSystemUser(lstAlunos, schoolYearObj)
                # print(dicAlunosScheduleDic)

                for aluno, scheduleDic in dicAlunosScheduleDic.items():
                    # scheduleDic-> {'1sem' : sem1SubjsStr, '2sem': sem2SubjsStr}

                    dic1semOrdend = ordenar_horario(scheduleDic['1sem'])
                    dic2semOrdend = ordenar_horario(scheduleDic['2sem'])

                    sobrep1sem = aulas_sobrepostas_horario(dic1semOrdend, mySubjectsName)
                    sobrep2sem = aulas_sobrepostas_horario(dic2semOrdend, mySubjectsName)

                    # testar
                    # sobrep1sem.append(['sexta', ['10:00', '1:30', 'aaaaaa', 'T', '18', '1.1.12'], ['11:00', '1:30', 'wwwwwww', 'TP', '19', '1.1.13']])
                    # sobrep2sem= [['Quinta', ['10:00', '1:30', 'adasd', 'T', '12', '1.1.12'], ['11:00', '1:30', 'jhwjhd', 'TP', '13', '1.1.13']]]

                    if sobrep1sem or sobrep2sem:  # se o aluno tiver sobreposiçoes
                        dicAlunosSobreposicoes[aluno] = {1: sobrep1sem, 2: sobrep2sem}
            else:
                dicAlunosSobreposicoes = {}

            # print(dicAlunosSobreposicoes)
            return render(request, 'teacher/home.html', {"suRegentes": regentes, "typesAndLessons": my_dictionary,
                                                         "NumStdBySub": NumberOfStudentsList,
                                                         "myTeachersBoyy": TrueFinalList,
                                                         "dicAlunosSobrepo": dicAlunosSobreposicoes})
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))

            # horario cadeira, prim pedido ajax
            if 'nomeCadeira' in dadosJson:
                nomeCadeira = dadosJson['nomeCadeira']
                print(nomeCadeira)
                schedule = buildHorarioSubject(nomeCadeira)
                return HttpResponse(json.dumps({"message": "success", 'schedule': schedule}),
                                    content_type="application/json")

            # horario aluno, seg pedido ajax
            else:
                alunoFc = dadosJson['aluno']
                print(alunoFc)
                u = User.objects.get(username=alunoFc)
                su = SystemUser.objects.get(user=u)
                schoolYearObj = SchoolYear.objects.get(begin=2018)
                subjsNameDict, scheduleDict = buildHorarioSystemUser("Aluno", su, schoolYearObj)
                return HttpResponse(
                    json.dumps({"message": "success", 'scheduleDict': scheduleDict, 'subjsName': subjsNameDict}),
                    content_type="application/json")


    else:
        return HttpResponseRedirect(reverse('login'))


def consult_contacts_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):

        profRole = Role.objects.get(role="Professor")
        AllTeachers = SystemUser.objects.filter(role=profRole)
        AllTeachersProfiles = []

        for prof in AllTeachers:
            endmeplz = Subject.objects.filter(regente=prof)
            subReg = ", ".join(([sub.name for sub in endmeplz]))

            if len(subReg) == 2:
                subReg = ""

            AllTeachersProfiles.append((PersonalInfo.objects.get(user=prof), subReg))

        return render(request, 'teacher/consult_contacts.html', {"Teachers": AllTeachersProfiles})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_details_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        consult_details_post(request)
        return render(request, 'teacher/consult_details.html', {})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_turmas_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == 'GET':
            semestre = getAllTypesturmasBySubjsGiveByTeacher(su, schoolYearObj)

            # 'scheduleDict':{}, 'subjsName':{}-> para nao dar erro no js
            return render(request, 'teacher/consult_turmas_D.html',
                          {'subjsSem': semestre, 'scheduleDict': {}, 'subjsName': {}})
        else:
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)

            # prim pedido ajax post
            if 'aluno' not in dadosJson:
                sem = dadosJson['sem']
                subj = Subject.objects.get(name=dadosJson['subjName'])
                listAlunos = getAlunosOfClassInSpecificSubj(sem, subj, dadosJson['typeTurma'], schoolYearObj)
                return HttpResponse(json.dumps({"message": "success", "JSONalunos": listAlunos}),
                                    content_type="application/json")

            # seg pedido ajax post (ver horario aluno)
            else:
                alunoFc = dadosJson['aluno']
                print(alunoFc)
                u = User.objects.get(username=alunoFc)
                su = SystemUser.objects.get(user=u)
                schoolYearObj = SchoolYear.objects.get(begin=2018)
                subjsNameDict, scheduleDict = buildHorarioSystemUser("Aluno", su, schoolYearObj)
                return HttpResponse(
                    json.dumps({"message": "success", 'scheduleDict': scheduleDict, 'subjsName': subjsNameDict}),
                    content_type="application/json")

    else:
        return HttpResponseRedirect(reverse('login'))


def alterar_turmas_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):

        class FearAllWhoCodeThis:

            def __init__(self, tab_name, sub_name, classes_num_student):
                self.id = "#" + tab_name
                self.idNoHashTag = tab_name
                self.subjectName = sub_name
                self.classesDict = classes_num_student

        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == "GET":

            iTeachedThese = list(Lesson.objects \
                                 .filter(professor=su) \
                                 .values("subject__name", "type", "turma", "is_open").distinct())

            i_teached_these_list = []

            just_the_subjects = []

            for line in iTeachedThese:
                i_teached_these_list.append((line["subject__name"], line["type"] + line["turma"], line["is_open"]))
                just_the_subjects.append(line["subject__name"])

            ohgod = list(SystemUserSubject.objects \
                         .filter(anoLetivo=schoolYearObj, subject__name__in=just_the_subjects) \
                         .values("user", "subject__name", "turmas").distinct())

            sweet_baby_jesus = []
            from itertools import groupby

            i = 1
            finalList = []

            for sub_name, g in groupby(ohgod, lambda a: a["subject__name"]):

                myList = []

                for tuple in i_teached_these_list:

                    if tuple[0] == sub_name:

                        num_students = 0
                        a = copy.deepcopy(g)

                        for d in list(a):

                            if tuple[1] in d["turmas"]:
                                num_students += 1

                        myList.append((tuple[1], num_students, tuple[2]))

                finalList.append(FearAllWhoCodeThis("tab" + str(i), sub_name, myList))
                i += 1

            return render(request, 'teacher/alterar_turmas.html', {"finalList": finalList})

        elif request.method == 'POST':

            dadosJson = json.loads(request.body.decode("utf-8"))

            inf = dadosJson['info']
            my_pretty_info = inf.split("|")

            aaaaah = list(
                Lesson.objects.filter(subject__name=my_pretty_info[0], type=separateLettersNumb(my_pretty_info[1])[0],
                                      turma=separateLettersNumb(my_pretty_info[1])[1]))

            for line in aaaaah:
                if my_pretty_info[2] == "True":
                    line.is_open = False
                elif my_pretty_info[2] == "False":
                    line.is_open = True
                line.save()

            return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")

    else:
        return HttpResponseRedirect(reverse('login'))


def resposta_pedidos_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        if request.method == "GET":
            su = request_user(request)
            pedidos = list(SystemUserMensagens.objects.filter(destinatario=su))

            listPedidos = []
            historicoPedidos = []
            for p in pedidos:
                student = PersonalInfo.objects.get(user=p.remetente)
                subj = p.subject
                startClass = p.turmaInicial
                finalClass = p.turmaFinal
                status = p.is_accepted
                if status == True or status == False:
                    historicoPedidos.append((student, subj, startClass, finalClass, status))
                else:
                    listPedidos.append((student, subj, startClass, finalClass, status))

            pedidosSent = list(SystemUserMensagens.objects.filter(remetente=su))
            pedidosS = []
            for ap in pedidosSent:
                student = PersonalInfo.objects.get(user=ap.destinatario)
                subj = ap.subject
                startClass = ap.turmaInicial
                finalClass = ap.turmaFinal
                status = ap.is_accepted
                if status != True and status != False:
                    status = "Enviado"
                pedidosS.append((student, subj, startClass, finalClass, status))

            return render(request, 'teacher/resposta_pedidos_D.html',
                          {"listPedidos": listPedidos, "historicoPedidos": historicoPedidos, "pedidosS": pedidosS})

        elif request.method == "POST":
            dadosJson = json.loads(request.body.decode("utf-8"))

            inf = dadosJson['info']
            info = inf.split("|")

            studentSystem = PersonalInfo.objects.get(name=info[1])
            subjSystem = Subject.objects.get(name=info[0])
            initial = info[2]
            final = info[3]

            update = SystemUserMensagens.objects.get(subject=subjSystem, remetente=studentSystem.user,
                                                     turmaInicial=initial, turmaFinal=final)

            if info[4] == "True":
                update.is_accepted = True

                pedidos = SystemUserSubject.objects.get(user=studentSystem.user, subject=subjSystem)
                turmas = pedidos.turmas.split()
                for t in turmas:
                    if t == initial:
                        turmas.pop(turmas.index(t))
                        turmas.append(final)
                        break
                turmasStr = " ".join(turmas)
                pedidos.turmas = turmasStr
                pedidos.save()

            elif info[4] == "False":
                update.is_accepted = False

            update.save()

            return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")
    else:
        return HttpResponseRedirect(reverse('login'))


def enviar_pedidos_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == "GET":
            # ex: retorna-> [14514, 14538, ..., 15196]
            lstAlunos = []
            lessons = Lesson.objects.filter(professor=su).values("subject__name", "type", "turma").distinct()
            # print(lessons)
            # print(lessons.count())

            formatDicBySubj = {}
            for subjName, typeTurma in groupby(lessons, lambda a: a["subject__name"]):
                # print(subjName)
                # print(typeTurma) #{'subject__name': 'Aplicações Distribuídas', 'type': 'TP', 'turma': '24'}

                SubjturmasByTeacher = []  # turmas lecionadas pelo prof
                lstTypeTurmasQuerie = []
                for dic in typeTurma:
                    lstTypeTurmasQuerie.append(Q(turmas__contains=dic["type"] + dic["turma"]))
                    SubjturmasByTeacher.append(dic["type"] + dic["turma"])

                Subjturmas = Lesson.objects.filter(subject__name=subjName).values('type', 'turma').distinct()
                print(Subjturmas)
                # [{'type': 'TP', 'turma': '12'}, ... ]

                # print(lstTypeTurmasQuerie)
                lstSuObjs = list(SystemUserSubject.objects.filter(
                    Q(subject__name=subjName) & Q(anoLetivo=schoolYearObj) & (
                        reduce(operator.or_, lstTypeTurmasQuerie))).values("user", "turmas"))
                # print(lstSuObjs)
                # ex: [{'user': 117, 'turmas': 'T11 TP12'}, {'user': 128, 'turmas': 'T11 TP12'}

                if lstSuObjs:
                    lstSuQueries2 = []

                    for suObj in lstSuObjs:
                        lstSuQueries2.append(Q(user=suObj['user']))

                    lstPI = PersonalInfo.objects.filter(reduce(operator.or_, lstSuQueries2)).values(
                        "user__user__username", "name")

                    formatDicBySU = {}
                    # len(systemUsersObjs) == len(lstPIName)
                    for i in range(0, len(lstPI)):
                        suFC = lstPI[i]["user__user__username"]
                        suName = lstPI[i]["name"]

                        lstTurmasAluno = lstSuObjs[i]['turmas'].split(" ")
                        lstTurmasAlunosSemEspaços = [e for e in lstTurmasAluno if e != ""]

                        lstTurmasFiltradas = []
                        for dicTurma in Subjturmas:
                            turma = dicTurma['type'] + dicTurma['turma']
                            if turma not in lstTurmasAlunosSemEspaços:
                                lstTurmasFiltradas.append(turma)

                        formatDicBySU[suFC + " | " + suName] = [lstTurmasAlunosSemEspaços, lstTurmasFiltradas]

                formatDicBySubj[subjName] = [SubjturmasByTeacher, formatDicBySU]

            # print(formatDicBySubj)
            # formatDicBySubj-> {'Controvérsias Científicas': [[T11, TP12], {"fc117 | Rute M": [['T11', 'TP11'], [turmas filtradas], "fc117 | Helder C" : [...] }], 'Programação II (LTI)': [[..],{...}]}
            return render(request, 'teacher/enviar_pedido.html', {'formatDicBySubj': formatDicBySubj})

        elif request.method == "POST":
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)
            infoAluno = dadosJson['alunoEscolhido']

            try:
                valid = True
                alunoFc, nome = infoAluno.split(" | ")
                u = User.objects.get(username=alunoFc)
                suAluno = SystemUser.objects.get(user=u)
                subj = Subject.objects.get(name=dadosJson['mySub'])
                old_class = dadosJson['turma']
                new_class = dadosJson['novaTurma']

                lsttTypeTurmaOldClass = separateLettersNumb(old_class)
                lsttTypeTurmaNewClass = separateLettersNumb(new_class)

                suMensagens = SystemUserMensagens.objects.filter(remetente=su, destinatario=suAluno, subject=subj,
                                                                 turmaInicial=old_class).values("is_accepted")
                print(suMensagens)
                for suMsg in suMensagens:
                    if suMsg['is_accepted'] == None:
                        valid = False

                if lsttTypeTurmaOldClass[0] != lsttTypeTurmaNewClass[0]:
                    valid = False

                if valid:
                    newSysUserMens = SystemUserMensagens(remetente=su, destinatario=suAluno, subject=subj,
                                                         turmaInicial=old_class, turmaFinal=new_class)
                    newSysUserMens.save()
                    return HttpResponse(json.dumps({"message": "success"}), content_type="application/json")

                else:
                    return HttpResponse(json.dumps({"message": "failure"}), content_type="application/json")

            except Exception as e:
                return HttpResponse(json.dumps({"message": "failure"}), content_type="application/json")



    else:
        return HttpResponseRedirect(reverse('login'))


def presencas_consultar_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)
        if request.method == 'GET':
            semestre = getAllTypesturmasBySubjsGiveByTeacher(su, schoolYearObj)
            return render(request, 'teacher/presenças_consulta.html', {"subjsSem": semestre})
        else:  # pedido ajax post
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)

            """
                2018/2019
                    1º semestre: 17/09/2018(seg) a 19/12/2018(quarta)
                    2º semestre: 18/02/2019(seg) a 31/05/2019(sex)
            """

            sem = dadosJson['sem']
            if sem == "1":
                dataInicio = "17/09/2018"
                dataFinal = "19/12/2018"
                ano = "2018"
            else:
                dataInicio = "18/02/2019"
                dataFinal = "31/05/2019"
                ano = "2019"

            joinFerias = allFeriasDate(ferias, ano)
            formatFeriados = convertFeriados(feriados, ano)
            joinFeriasAndFeriados = joinFerias + formatFeriados
            infoSemPresenças = [dataInicio, dataFinal, joinFeriasAndFeriados]
            subj = Subject.objects.get(name=dadosJson['subjName'])
            listAlunos = getAlunosOfClassInSpecificSubj(sem, subj, dadosJson['typeTurma'], schoolYearObj,
                                                        infoSemPresenças)
            return HttpResponse(json.dumps({"message": "success", "JSONalunos": listAlunos}),
                                content_type="application/json")

    else:
        return HttpResponseRedirect(reverse('login'))


def presencas_registar_t(request):
    if is_authenticated(request, university.models.TEACHER_ROLE):
        su = request_user(request)
        schoolYearObj = SchoolYear.objects.get(begin=2018)

        if request.method == 'GET':
            suLessons = list(Lesson.objects.filter(professor=su))
            sem1SubjsStr = []
            sem2SubjsStr = []
            for lesson in suLessons:
                str = lesson.week_day + "," + lesson.hour + "," + lesson.subject.name + "," + lesson.type + "," + lesson.turma
                subj = lesson.subject
                CRsubjs = CourseSubject.objects.filter(subject=subj)

                # se o sem da cadeira e igual independentemente do curso
                if is_semestres_all_same(CRsubjs):
                    sem = CRsubjs[0].semester
                    if sem == 1:
                        sem1SubjsStr.append(str)
                    else:
                        sem2SubjsStr.append(str)

                else:
                    sem1SubjsStr.append(str)
                    sem2SubjsStr.append(str)

            print(sem1SubjsStr)
            print(sem2SubjsStr)
            scheduleDict = {'1sem': sem1SubjsStr, '2sem': sem2SubjsStr}
            return render(request, 'teacher/presenças_registo.html', {'scheduleDict': scheduleDict})

        else:
            dadosJson = json.loads(request.body.decode("utf-8"))
            print(dadosJson)

            # prim pedido ajax post
            if 'alunosEscolhidos' not in dadosJson:
                aulaEscolhidaInfo = dadosJson
                sem = aulaEscolhidaInfo['sem'][0]
                subjName = aulaEscolhidaInfo['cadeiraEscolhida']
                typeTurma = aulaEscolhidaInfo['turmaEscolhida']
                SubjObj = Subject.objects.get(name=subjName)
                listAlunos = getAlunosOfClassInSpecificSubj(sem, SubjObj, typeTurma, schoolYearObj)
                return HttpResponse(json.dumps({"message": "success", "alunos": listAlunos}),
                                    content_type="application/json")

            # seg pedido ajax post
            else:
                alunosEscolhidosInfo = dadosJson
                print(alunosEscolhidosInfo)
                alunosEscolhidos = alunosEscolhidosInfo['alunosEscolhidos']
                alunosNaoEscolhidos = alunosEscolhidosInfo['alunosNaoEscolhidos']
                subjName = alunosEscolhidosInfo['cadeiraEscolhida']
                typeTurma = alunosEscolhidosInfo['turmaEscolhida']
                lsttTypeTurma = separateLettersNumb(typeTurma)
                week_day = alunosEscolhidosInfo['week_day']
                SubjObj = Subject.objects.get(name=subjName)
                lessonObj = Lesson.objects.get(subject=SubjObj, type=lsttTypeTurma[0], turma=lsttTypeTurma[1],
                                               week_day=week_day)
                date_str = dadosJson['date']
                dateFormat = datetime.strptime(date_str, "%d/%m/%Y").date()

                # remover dados que possam existir na bd naquela lesson naquele dia
                LessonSystemUser.objects.filter(lesson=lessonObj, date=dateFormat).delete()

                # tenho que criar novos dados, pq podem haver alunos novos nesta turma
                print(alunosEscolhidos)
                for alunoEsc in alunosEscolhidos:
                    userObj = User.objects.get(username=alunoEsc)
                    su = SystemUser.objects.get(user=userObj)
                    newLessonSU = LessonSystemUser(lesson=lessonObj, systemUser=su, presente=True, date=dateFormat)
                    newLessonSU.save()
                for alunoEsc in alunosNaoEscolhidos:
                    userObj = User.objects.get(username=alunoEsc)
                    su = SystemUser.objects.get(user=userObj)
                    newLessonSU = LessonSystemUser(lesson=lessonObj, systemUser=su, presente=False, date=dateFormat)
                    newLessonSU.save()
                return HttpResponse('')


    else:
        return HttpResponseRedirect(reverse('login'))


# ------------------------------------------------ Funçoes auxiliares Teacher ------------------------------------------------
lstDiasDaSemana = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
feriados = ['01/01', '19/04', '21/04', '25/04', '01/05', '10/06', '20/06', '15/08', '05/10', '01/11', '01/12', '08/12',
            '25/12']  # completo
ferias = [["04/03", "06/03"],  # carnaval
          ["17/04", "23/04"]]  # pascoa


def getAlunosOfClassInSpecificSubj(sem, subj, typeTurma, schoolYearObj, infoSemPresenças=[]):
    # ex: 1, AD, T11, 2018
    # obtem todos os alunos que pertencem a uma turma de uma determinada cadeira
    # retorna em json uma lista de listas, em q cada lista tem informaçao sobre um aluno

    systemUsersObjs = list(
        SystemUserSubject.objects.filter(subject=subj, turmas__contains=typeTurma, anoLetivo=schoolYearObj,
                                         subjSemestre=sem))
    # systemUsersObjs -> ex: [<SystemUserSubject: SystemUserSubject object (1579)>, ... ]

    if systemUsersObjs:  # se houverem alunos inscritos

        print(infoSemPresenças)
        if infoSemPresenças:
            lstDates = getAllDatasByTypeturmaSubj2018_2019(subj, typeTurma, infoSemPresenças)
            print(lstDates)  # ex: ['19/02/2019', '20/02/2019', ...]
            lstDataFormatsQueries = []
            for date_str in lstDates:
                dataFormat = datetime.strptime(date_str, "%d/%m/%Y").date()
                lstDataFormatsQueries.append(Q(date=dataFormat))

            type, turma = separateLettersNumb(typeTurma)
            myListOfCollegues = [lstDates]
        else:
            myListOfCollegues = []

        lstSuQueries1 = []
        lstSuQueries2 = []
        for suObj in systemUsersObjs:
            lstSuQueries1.append(Q(user=suObj.user))
            lstSuQueries2.append(Q(systemUser=suObj.user))

        lstPIName = PersonalInfo.objects.filter(reduce(operator.or_, lstSuQueries1)).values("name")
        # lstPIName -> ex: [{'name': 'Kevin Maia'}, {'name': 'Camila Monteiro'}, ...]

        if infoSemPresenças:  # se nao for uma lista vazia
            # lista de presenças de um aluno
            listLessonsSU = LessonSystemUser.objects.filter(
                reduce(operator.or_, lstSuQueries2) & Q(lesson__type=type) & Q(lesson__subject=subj) & reduce(
                    operator.or_, lstDataFormatsQueries)).values("systemUser", "date", "presente")

            dicDates = {}
            for su, datePresent in groupby(listLessonsSU, lambda a: a["systemUser"]):
                # ex: [{'systemUser': 798, 'date': datetime.date(2018, 9, 18), 'presente': True}, {'systemUser': 798, 'date': datetime.date(2018, 9, 25), 'presente': True}]
                dates = {}
                for dic in list(datePresent):
                    dates[dic['date']] = dic['presente']
                dicDates[su] = dates

            # print(dicDates)
            # ex: {117: {datetime.date(2018, 9, 18): False, datetime.date(2018, 9, 25): True}, ...}

        # len(systemUsersObjs) == len(lstPIName)
        for i in range(0, len(lstPIName)):
            su = systemUsersObjs[i].user

            if infoSemPresenças:  # se nao for uma lista vazia

                lstPresencasAluno = []
                for date_str in lstDates:
                    dateFormat = datetime.strptime(date_str, "%d/%m/%Y").date()
                    if dicDates:  # se houver alguma presença
                        if dateFormat in dicDates[su.id]:
                            is_present = dicDates[su.id][dateFormat]
                            lstPresencasAluno.append(is_present)
                        else:
                            lstPresencasAluno.append("-")
                    else:
                        lstPresencasAluno.append("-")

                print(lstPresencasAluno)
                listInfo = [su.user.username, lstPIName[i]["name"], lstPresencasAluno]

            else:
                listInfo = [su.user.username, lstPIName[i]["name"], su.user.email]
                # listInfo ex: ['fc117', 'Kevin Maia', 'fc117@alunos.fc.ul.pt']

            myListOfCollegues.append(listInfo)

    else:
        myListOfCollegues = []

    return myListOfCollegues


def getAllDatasByTypeturmaSubj2018_2019(subj, typeTurma, infoSemPresenças):
    # ex: "T11", ["18/02/2019", "31/05/2019", joinFeriasAndFeriados]
    dataInicio, dataFinal, joinFeriasAndFeriados = infoSemPresenças
    type, turma = separateLettersNumb(typeTurma)
    turmaLessons = list(Lesson.objects.filter(subject=subj, type=type, turma=turma).values_list("week_day"))
    print(turmaLessons)
    diasDaSemanaStr = " ".join([tlesson[0] for tlesson in turmaLessons])
    print(diasDaSemanaStr)
    return getDatesBetween2Dates(dataInicio, dataFinal, joinFeriasAndFeriados, diasDaSemanaStr)


def getAllAlunosQueTemAulasComUmProf(systemUser, schoolYearObj):
    # ex: retorna-> [14514, 14538, ..., 15196]
    lstAlunos = []
    lessons = Lesson.objects.filter(professor=systemUser).values("subject__name", "type", "turma").distinct()
    # print(lessons)
    # print(lessons.count())

    for subjName, typeTurma in groupby(lessons, lambda a: a["subject__name"]):
        # print(subjName)
        # print(typeTurma) #{'subject__name': 'Aplicações Distribuídas', 'type': 'TP', 'turma': '24'}
        lstTypeTurmasQuerie = []
        for dic in typeTurma:
            lstTypeTurmasQuerie.append(Q(turmas__contains=dic["type"] + dic["turma"]))

        # print(lstTypeTurmasQuerie)
        suObjs = list(SystemUserSubject.objects.filter(Q(subject__name=subjName) & Q(anoLetivo=schoolYearObj) & (
            reduce(operator.or_, lstTypeTurmasQuerie))).values("user"))

        lstAlunos += suObjs

    # print(lstAlunos)
    # print(len(lstAlunos))

    # elementos unicos de uma lista
    lstAlunosUnique = []
    for dic in lstAlunos:
        if dic["user"] not in lstAlunosUnique:
            lstAlunosUnique.append(dic["user"])

    # print(lstAlunosUnique)
    # print(len(lstAlunosUnique))
    return lstAlunosUnique


def getAllTypesturmasBySubjsGiveByTeacher(systemUser, schoolYearObj):
    # ex: ensures-> {1: {sub1Obj: {'T': [11, 12]},
    #                   sub2Obj: {...}
    #                   },
    #               2: {...}
    #               }
    suLessons = Lesson.objects.filter(professor=systemUser).values("subject", "type", "turma").distinct()

    dic1SemSubjs = {}
    dic2SemSubjs = {}

    for subj_id, typeTurma in groupby(suLessons, lambda a: a["subject"]):
        subj = Subject.objects.get(id=subj_id)
        # print(typeTurma) #{'subj_id': 7, 'type': 'TP', 'turma': '24'}
        dicTypeTurmas = {}
        for dic in typeTurma:
            if dic["type"] not in dicTypeTurmas:
                dicTypeTurmas[dic["type"]] = [dic["turma"]]
            else:
                dicTypeTurmas[dic["type"]].append(dic["turma"])

        CRsubjs = CourseSubject.objects.filter(subject=subj)

        # por a cadeira na listaSemestre certo com as respetivas Turmas

        # se o sem da cadeira e igual independentemente do curso
        if is_semestres_all_same(CRsubjs):
            sem = CRsubjs[0].semester
            if sem == 1:
                dic1SemSubjs[subj] = dicTypeTurmas
            else:
                dic2SemSubjs[subj] = dicTypeTurmas
        else:
            dic1SemSubjs[subj] = dicTypeTurmas
            dic2SemSubjs[subj] = dicTypeTurmas

    print(dic1SemSubjs)
    print(dic2SemSubjs)

    return {"1": dic1SemSubjs, "2": dic2SemSubjs}


# --------------------------------------------------------------------------------------------------------------------------------
#                                                        ADMIN
# --------------------------------------------------------------------------------------------------------------------------------
def home_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        return render(request, 'admin/index.html', {})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        # print(app_list)
        return render(request, 'admin/consult.html', {'app_list': app_list})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_auth_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/consult.html', {'app_list': [app_list[0]]})
    else:
        return HttpResponseRedirect(reverse('login'))


def consult_uni_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/consult.html', {'app_list': [app_list[1]]})
    else:
        return HttpResponseRedirect(reverse('login'))


def insert_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/insert.html', {'app_list': app_list})
    else:
        return HttpResponseRedirect(reverse('login'))


def operacoesBloco_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        if request.method == 'POST':
            if request.FILES.get('file_sql', False):
                valid = "yapp"
                myfile = request.FILES['file_sql']

                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
                uploaded_file_url = fs.url(filename)  # gets the url

                with connection.cursor() as cursor:
                    try:
                        for line in open(uploaded_file_url):
                            if line != "\n" and len(line) > 5 and line[
                                0] != "-":  # para ignorar as linhas em branco ou so com espaços ou start with '-'
                                cursor.execute(line)
                    except Exception as e:
                        messages.error(request, "O ficheiro contem erros!")
                        valid = "error"

                fs.delete(myfile.name)



            else:
                valid = "empty"
            return render(request, 'admin/oper_bloco.html', {'uploaded': valid})
        elif request.method == 'GET':
            return render(request, 'admin/oper_bloco.html')
    else:
        return HttpResponseRedirect(reverse('login'))


def export_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        admin_index = admin.site.index(request)
        app_list = admin_index.context_data['app_list']
        return render(request, 'admin/export.html', {'app_list': [app_list[1]]})
    else:
        return HttpResponseRedirect(reverse('login'))


# --------------- teacher and student ---------------

def consult_details_post(request):
    if request.method == 'POST':
        su = request_user(request)
        PIObject = PersonalInfo.objects.get(user=su)

        dic = dict(request.POST)
        dic.pop('csrfmiddlewaretoken')
        print(dic)
        keyName = list(dic)[0]
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

        if (roleName == "Admin"):
            return HttpResponseRedirect(reverse('login'))
        elif (roleName == "Professor"):
            if current_url != "horario_atual_t":
                return HttpResponseRedirect(reverse('horario_atual_t'))
            base_template = "teacher/base_t.html"
        else:
            if current_url != "horario_atual_s":
                return HttpResponseRedirect(reverse('horario_atual_s'))
            base_template = "student/base_s.html"

        schoolYearObj = SchoolYear.objects.get(begin=2018)
        subjsNameDict, scheduleDict = buildHorarioSystemUser(roleName, su, schoolYearObj)
        return render(request, 'horario.html',
                      {'base_template': base_template, 'scheduleDict': scheduleDict, 'subjsName': subjsNameDict})
    else:
        return HttpResponseRedirect(reverse('login'))


def separateLettersNumb(string):
    # "TP13" fica ['TP', '13']
    return re.split('(\d+)', string)[:-1]


def is_semestres_all_same(courseSubjs):
    return all(crS.semester == courseSubjs[0].semester for crS in courseSubjs)


def getsystemUsersSemSubjTypTurmas(lstAlunos, schoolYearObj):
    # ensures ->   ex:
    # systemUserSemSubjTypTurmas       [[117, {'1sem': [['Controvérsias Científicas', 'T11 TP11'], ... ],
    #            '2sem': [['Programação II (LTI)', 'T21 TP25 PL26'], ... ]}],
    #        ...]

    # print(lstAlunos)
    lstAlunosQuerie = []
    for alunos in lstAlunos:
        lstAlunosQuerie.append(Q(user=alunos))

    suSubjs = SystemUserSubject.objects.filter(
        reduce(operator.or_, lstAlunosQuerie) & Q(anoLetivo=schoolYearObj)).values("user", "subject__name",
                                                                                   "subjSemestre", "turmas")

    systemUserSemSubjTypTurmas = []
    lstSubjTurmasQuerie = []
    for systemUser, semSubjNameTurmasStr in groupby(suSubjs, lambda a: a["user"]):
        lst1semSubjsTypeTurmasStr = []
        lst2semSubjsTypeTurmasStr = []

        for subjSemestre, subjNameTurmasStr in groupby(semSubjNameTurmasStr, lambda a: a["subjSemestre"]):
            sem = subjSemestre

            for subjName, TurmasStr in groupby(subjNameTurmasStr, lambda a: a["subject__name"]):
                # print(subjName)
                lessons = []
                lstTypeTurmasQuerie = []

                for dic in TurmasStr:
                    lstTurmas = dic["turmas"].split(" ")
                    lstTurmasSemEspaços = [e for e in lstTurmas if e != ""]
                    # ex: lstTurmasSemEspaços-> ["T11","TP13","PL13"]

                    # todas as turmas em q o aluno esta inscrito numa cadeira
                    for typeTurma in lstTurmasSemEspaços:
                        type, turma = separateLettersNumb(typeTurma)
                        lstTypeTurmasQuerie.append(Q(type=type) & Q(turma=turma))

                lstSubjTurmasQuerie.append(Q(subject__name=subjName) & reduce(operator.or_, lstTypeTurmasQuerie))

                if sem == 1:
                    lst1semSubjsTypeTurmasStr.append([subjName, dic["turmas"]])
                else:
                    lst2semSubjsTypeTurmasStr.append([subjName, dic["turmas"]])

        systemUserSemSubjTypTurmas.append(
            [systemUser, {'1sem': lst1semSubjsTypeTurmasStr, '2sem': lst2semSubjsTypeTurmasStr}])

    # print(systemUserSemSubjTypTurmas)
    return [systemUserSemSubjTypTurmas, lstSubjTurmasQuerie]


def buildHorarioLstSystemUser(lstAlunos, schoolYearObj):
    # ex: lstAlunos é uma lista de systemUsers
    # ex: ensures: dicSytemUsersHorarios= {aluno1: scheduleDict, aluno2: scheduleDict , ...}

    systemUserSemSubjTypTurmas, lstSubjTurmasQuerie = getsystemUsersSemSubjTypTurmas(lstAlunos, schoolYearObj)

    turmaLessonsPossiveis = Lesson.objects.filter(reduce(operator.or_, lstSubjTurmasQuerie)).values("subject__name",
                                                                                                    "type", "turma",
                                                                                                    "week_day", "hour",
                                                                                                    "duration",
                                                                                                    "room__room_number")
    print(1212)
    print(turmaLessonsPossiveis)

    dicSytemUsersHorarios = {}
    for subjName, rest1 in groupby(turmaLessonsPossiveis, lambda a: a["subject__name"]):

        for typeTurma, rest2 in groupby(rest1, lambda a: a["type"] + a["turma"]):
            # ex: typeTurma -> T11

            lessons = []
            for dic in rest2:  # AD T11 terça, AD T11 quinta
                # dic ex: {'subject__name': 'Programação II (LTI)', 'type': 'T', 'turma': '21', 'week_day': 'SEGUNDA', 'hour': '08:00', 'duration': '1:00', 'room__room_number': '1.5.64'}
                str = dic["week_day"] + "," + dic["hour"] + "," + dic["duration"] + "," + subjName + "," + dic[
                    "type"] + "," + dic["turma"] + "," + dic["room__room_number"]
                lessons.append(str)

            # distribuir a lesson pelos alunos corretos
            for suSemSubjs in systemUserSemSubjTypTurmas:
                for sem, lstSubjs in suSemSubjs[1].items():
                    for lst in lstSubjs:
                        if lst[0] == subjName and typeTurma in lst[1]:
                            if suSemSubjs[0] not in dicSytemUsersHorarios:
                                dicSytemUsersHorarios[suSemSubjs[0]] = {'1sem': [], '2sem': []}
                            dicSytemUsersHorarios[suSemSubjs[0]][sem] = dicSytemUsersHorarios[suSemSubjs[0]][
                                                                            sem] + lessons

    return dicSytemUsersHorarios


def buildHorarioSystemUser(roleName, systemUser, schoolYearObj):
    # ex: ensures sem1SubjsStr:
    # ['QUINTA,08:00,1:00,Programação I (LTI),T,2.1.10', 'QUINTA,09:00,1:30,Programação I (LTI),PL,2.1.11',
    # 'QUINTA,10:30,1:30,Programação I (LTI),PL,2.1.10', 'QUINTA,12:00,1:30,Programação I (LTI),PL,2.1.11',
    # 'QUARTA,08:00,1:30,Programação I (LTI),TP,1.5.64', 'QUARTA,09:30,1:30,Programação I (LTI),TP,1.5.63']

    sem1SubjsStr = []
    sem2SubjsStr = []
    sem1subjsName = []
    sem2subjsName = []

    # aluno
    if roleName == "Aluno":
        # todas as cadeiras que o aluno esta inscrito neste ano
        suSubjs = SystemUserSubject.objects.filter(user=systemUser, anoLetivo=schoolYearObj).values("subject__name",
                                                                                                    "subjSemestre",
                                                                                                    "turmas")

        for subjSemestre, subjNameTurmasStr in groupby(suSubjs, lambda a: a["subjSemestre"]):
            sem = subjSemestre

            lstSubjTurmasQuerie = []
            for subjName, TurmasStr in groupby(subjNameTurmasStr, lambda a: a["subject__name"]):
                print(subjName)
                lessons = []
                lstTypeTurmasQuerie = []

                for dic in TurmasStr:
                    lstTurmas = dic["turmas"].split(" ")
                    lstTurmasSemEspaços = [e for e in lstTurmas if e != ""]
                    # ex: lstTurmasSemEspaços-> ["T11","TP13","PL13"]

                    # todas as turmas em q o aluno esta inscrito numa cadeira
                    for typeTurma in lstTurmasSemEspaços:
                        type, turma = separateLettersNumb(typeTurma)
                        lstTypeTurmasQuerie.append(Q(type=type) & Q(turma=turma))

                lstSubjTurmasQuerie.append(Q(subject__name=subjName) & reduce(operator.or_, lstTypeTurmasQuerie))
                if sem == 1:
                    sem1subjsName.append(subjName)
                else:
                    sem2subjsName.append(subjName)

            turmaLessons = list(Lesson.objects.filter(reduce(operator.or_, lstSubjTurmasQuerie)))
            for lesson in turmaLessons:
                str = lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
                lessons.append(str)

            if sem == 1:
                sem1SubjsStr = sem1SubjsStr + lessons
            else:
                sem2SubjsStr = sem2SubjsStr + lessons


    # professor
    else:
        suLessons = list(Lesson.objects.filter(professor=systemUser))
        for lesson in suLessons:
            str = lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
            subj = lesson.subject
            CRsubjs = CourseSubject.objects.filter(subject=subj)

            # se o sem da cadeira e igual independentemente do curso
            if is_semestres_all_same(CRsubjs):
                sem = CRsubjs[0].semester
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
    subjsNameDict = {'1sem': sem1subjsName, '2sem': sem2subjsName}
    scheduleDict = {'1sem': sem1SubjsStr, '2sem': sem2SubjsStr}
    return [subjsNameDict, scheduleDict]


def buildHorarioSubject(nameSubj):
    subjectObj = Subject.objects.get(name=nameSubj)
    lessons = list(Lesson.objects.filter(subject=subjectObj))
    lstLessonsStr = []

    for lesson in lessons:
        str = lesson.week_day + "," + lesson.hour + "," + lesson.duration + "," + lesson.subject.name + "," + lesson.type + "," + lesson.room.room_number
        lstLessonsStr.append(str)

    return lstLessonsStr


# ------------------------------------------------ Funçoes auxiliares Datas ------------------------------------------------

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
    start_date = datetime.strptime(dataInicio, '%d/%m/%Y')
    end_date = datetime.strptime(dataFinal, '%d/%m/%Y')

    if lazyDays == None:
        lstDates = []
    else:
        lstWorkDates = []

    for i in range(-1, (end_date - start_date).days, 1):
        nextDate = start_date + timedelta(days=i + 1)
        diaDaSemana = lstDiasDaSemana[nextDate.weekday()]
        if diaDaSemana in diasDaSemana:
            date_str = nextDate.date().strftime('%d/%m/%Y')
            # print(date_str)
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
    # recebe ex: ferias= [["04/03", "06/03"], ["17/04", "23/04"]], ano=2018
    # retorna ex: [['04/03/201*', '06/03/201*'], ['17/04/201*', '23/04/201*']]
    return list(map(lambda lst: list(map(lambda dm: dm + "/" + ano, lst)), ferias))


def convertFeriados(feriados, ano):
    # recebe ex: feriados = ['01/01', '19/04', ... ], ano=2018
    # retorna ex: feriados = ['01/01/201*', '19/04/201*', '21/04/201*', ...]
    return list(map(lambda dm: dm + "/" + ano, feriados))


def allFeriasDate(ferias, ano):
    # recebe ex: ferias= [["04/03", "06/03"], ["17/04", "23/04"]], ano=2018
    # retorna ex: ['04/03/2018', '05/03/2018', '06/03/2018', '17/04/2018', '18/04/2018', ... , '23/04/2018']
    newFerias = convertFerias(ferias, ano)
    newFerias_str = []
    for f in newFerias:
        dataInicio, dataFinal = f
        newFerias_str = newFerias_str + getDatesBetween2Dates(dataInicio, dataFinal)
    return newFerias_str


# ------------------------------------------------ Funçoes auxiliares Sobreposiçoes ------------------------------------------------
def ordenar_horario(lstLessonsStr):
    """
    requires: ['QUARTA,11:00,1:00,Redes de Computadores (LTI),T,11,1.5.67', 'QUINTA,09:30,1:00,Redes de Computadores (LTI),T,11,2.1.14',
              'QUINTA,08:00,1:30,Redes de Computadores (LTI),TP,11,2.1.15', 'TERÇA,09:00,2:00,Segurança Informática,T,11,2.1.12',
              'TERÇA,11:00,1:30,Segurança Informática,TP,11,2.1.11']

    ensures: {
              'QUARTA': [['11:00', '1:00', 'Redes de Computadores (LTI)', 'T', '11', '1.5.67']],
              'QUINTA': [['08:00', '1:30', 'Redes de Computadores (LTI)', 'TP', '11', '2.1.15'], ['09:30', '1:00', 'Redes de Computadores (LTI)', 'T', '11', '2.1.14']],
              'TERÇA': [['09:00', '2:00', 'Segurança Informática', 'T', '11', '2.1.12'], ['11:00', '1:30', 'Segurança Informática', 'TP', '11', '2.1.11']]
              }
    """
    lstlessons = []
    for lessonStr in lstLessonsStr:
        lesson = lessonStr.split(",")
        lstlessons.append(lesson)

    scheduleDict = {}

    for lesson in lstlessons:
        if lesson[0] in scheduleDict:
            scheduleDict[lesson[0]].append(lesson[1:])
        else:
            scheduleDict[lesson[0]] = [lesson[1:]]

    # print(scheduleDict)

    # Importante: para o mesmo dia de semana, as aulas TEM QUE ESTAR POR ORDEM!! (by time)
    # tenho q formatar primeiro a hora e depois ordenar
    for weekDay, lessons in scheduleDict.items():
        scheduleDict[weekDay] = sorted(lessons)

    # print(scheduleDict)
    return scheduleDict


def aulas_sobrepostas_horario(scheduleDict, checkLstCadeiras=[]):
    """
    se checkLstCadeiras == [] entao ele devolve todas as sobreposiçoes do horario
    se checkLstCadeiras != [] entao ele devolve apenas as sobreposiçoes que envolvem cadeiras que estao nessa lista
      requires: {
                'QUARTA': [['11:00', '1:00', 'Redes de Computadores (LTI)', 'T', '11', '1.5.67']],
                'QUINTA': [['08:00', '1:30', 'Redes de Computadores (LTI)', 'TP', '11', '2.1.15'], ['09:30', '1:00', 'Redes de Computadores (LTI)', 'T', '11', '2.1.14']],
                'TERÇA': [['09:00', '2:00', 'Segurança Informática', 'T', '11', '2.1.12'], ['11:00', '1:30', 'Segurança Informática', 'TP', '11', '2.1.11']]
                }

      ensures: [] ou
               [['TERÇA', ['08:00', '1:30', 'Segurança Informática', 'T', '11', '2.1.12'], ['09:00', '0:00', 'Segurança Informática', 'TP', '11', '2.1.11']]] ou
               [['QUINTA', ['08:00', '1:00', 'Redes de Computadores (LTI)', 'T', '11', '2.1.14'], ['08:00', '2:00', 'Redes de Computadores (LTI)', 'TP', '11', '2.1.15']], ['TERÇA', ['08:00', '2:00', 'Segurança Informática', 'T', '11', '2.1.12'], ['08:00', '3:30', 'Segurança Informática', 'TP', '11', '2.1.11']]]
      """
    sobreposicoes = []
    for weekDay, lstLessons in scheduleDict.items():
        if len(lstLessons) > 1:
            primLesson = True
            for lesson in lstLessons:
                if primLesson:
                    lessonToCompare = lesson
                    primLesson = False
                else:
                    if is_lesson1_and_lesson2_sobrepostas(lessonToCompare, lesson):
                        if checkLstCadeiras:
                            if lessonToCompare[2] in checkLstCadeiras or lesson[2] in checkLstCadeiras:
                                sobreposicoes.append([weekDay, lessonToCompare, lesson])
                        else:
                            sobreposicoes.append([weekDay, lessonToCompare, lesson])
                    lessonToCompare = lesson
    return sobreposicoes


def is_lesson1_and_lesson2_sobrepostas(lesson1, lesson2):
    return addMinutes(lesson1[0], lesson1[1]) > hourToMinutes(lesson2[0])


def hourToMinutes(hour):
    # ex: hour-> "9:00" ou "09:00"
    lhour = hour.split(":")
    return int(lhour[0]) * 60 + int(lhour[1])


def addMinutes(hour, duration):
    return hourToMinutes(hour) + hourToMinutes(duration)


@require_http_methods(["POST"])
def import_database_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        up_file = request.FILES['file']
        print(up_file.name.endswith('.json'))

        if not up_file.name.endswith(".json"):
            return HttpResponse(json.dumps({'ok': False}))

        default_storage.delete('upload_db.json')
        default_storage.save('upload_db.json', ContentFile(up_file.read()))

        try:
            call_command('loaddata', 'upload_db.json')
        except Exception:
            return HttpResponse(json.dumps({'ok': False}))
        return HttpResponse(json.dumps({'ok': True}))
    else:
        return HttpResponseForbidden()


@require_http_methods(["POST"])
def export_database_a(request):
    if is_authenticated(request, university.models.ADMIN_ROLE):
        call_command('dumpdata', '-o', 'db.json')

        response = HttpResponse(open("db.json", "r"), content_type='application/json', )
        response['Content-Disposition'] = "filename=db.json"
        return response
    else:
        return HttpResponseForbidden()
