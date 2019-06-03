from django.db import migrations, transaction
from ..models import *
from django.conf import settings
import math
import random
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
import collections
import re
import ast








#the @transaction.atomic method decorator ensures the method operations are run in a single transaction.

@transaction.atomic
def makeSchoolYearOBJs(beginYear, endYear):
    """
    beginYear -> o primeiro ano em q se começa a guardar dados
    endYear -> o ano final(ou seja, este ano)
    endYear > beginYear
    """
    for i in range(endYear - beginYear):
        begin= str((beginYear+i))
        end= str((beginYear+i+1))
        newYear= SchoolYear(begin=begin, end=end) #ex: (2017, 2018)
        newYear.save()

#makeRoomOBJs(70, 0)
@transaction.atomic
def makeRoomOBJs(totalroomsClasses, totalroomsOffices):
    """
    totalroomsClasses -> total de salas em q ha aulas (int)
    totalroomsOffices -> total de gabinetes (ou salas em q nao ha aulas) (int)
    """
    #nota: 1 building has a maximum of 5 floors (75 rooms)
    #nota: 1 floor has a maximim of 15 rooms
    totalRomms= totalroomsClasses + totalroomsOffices
    roomsPlaced= 0
    roomsLeftToPlace= totalRomms
    numBuilding= 1
    while roomsLeftToPlace > 0 :
        roomsPlaced += makeBuilding(numBuilding, 5, 15, roomsLeftToPlace, totalroomsOffices)
        roomsLeftToPlace= totalRomms - roomsPlaced
        numBuilding += 1
                


def makeBuilding(numBuilding, numFloors, numOfRoomsPerFloor, totalRooms, totalroomsOffices):
    """
    numBuilding -> numero do edificio (int)
    numFloors -> numero maximo de pisos desse edificio (int)
    numOfRoomsPerFloor -> numero maximo de salas de cada piso (int)
    totalRooms -> total de salas desse edificio, incluindo gabinetes (int)
    totalroomsOffices -> total de gabinetes desse edificio (int)
    """
    cont= 0
    give_class= True
    for f in range(1, numFloors+1):
        for r in range(numOfRoomsPerFloor):
            if (totalRooms - cont) <= totalroomsOffices :
                give_class = False
            cont += 1
            room= str(numBuilding) + "." + str(f) + "." + str(cont)
            newRoom = Room(room_number=room, can_give_class=give_class) #ex: (3.1.15, True)
            newRoom.save()
            if (cont == totalRooms): return cont
    return cont
    

@transaction.atomic
def makeRoleOBJs():
    roles = ["Professor", "Aluno", "Admin"]
    for r in roles:
        newRole= Role(role=r)
        newRole.save()



@transaction.atomic
def makeSystemUserOBJs():
    allUsers= User.objects.all() #800 users
    gabinetes= Room.objects.filter(can_give_class= False) #42 gabinetes
    #roles objs
    rProfessor= Role.objects.get(role="Professor")
    rAluno= Role.objects.get(role="Aluno")
    rAdmin= Role.objects.get(role="Admin")

    #[totalusers , roles, tem gabinete?]
 
    totalUserRoles= [[3, rAdmin, True, "@admin.fc.ul.pt"], [110, rProfessor, True, "@professor.fc.ul.pt"], [687, rAluno, False, "@alunos.fc.ul.pt"]] 
                   #3+110=113;    800-113=687 resto
                   #num professores = num cadeiras (regente)


    cont=1
    i=0
    gab= 0
    for user in allUsers :
        total= sum([n for (n,l,b,d) in totalUserRoles[:(i+1)]]) 
        if cont > total :
            i += 1
        newUSER= SystemUser(user=user, role=totalUserRoles[i][1])
        newUSER.save() #tem q ser antes do rooms.add
        user.email = user.username + totalUserRoles[i][3]

        if totalUserRoles[i][2] :
            newUSER.rooms.add(gabinetes[gab])
            gab = (gab+1) % gabinetes.count() #array circular

        
        user.save()
        cont += 1 



@transaction.atomic
def makePersonalInfoOBJs():
    allSystemUsers= SystemUser.objects.all()
    with open(settings.MIGRATIONS_DATA_ROOT + "/NamesGenderNationalityBirthAdressVat800.txt", encoding="utf8") as rfile:
        listData = rfile.readlines()
    num= 0
    m = 0
    f = 0
    femList = getDicttOfGenderPics()["female"]
    maleList = getDicttOfGenderPics()["male"]
    for user in allSystemUsers :
        name, gender, nationality, date_str, address, vat =listData[num].split("||")
        email= name.split()[-1]+str(user.id)+random.choice(["@hotmail.com", "@gmail.com"]) #unique
        phone = "9" + str(random.randint(00000000,99999999)) #because they are in portugal so they need a pt phone number xd
        random.seed(user.id)
        idDocument= str(random.randint(00000000,99999999)) #unique
        date = datetime.strptime(date_str, "%d/%m/%Y").date()

        newUSER= PersonalInfo(user=user, address=address, birth_date=date, name=name,
                 phone_number=phone, personal_email=email, gender=gender, nationality=nationality, id_document=idDocument, vat_number=vat)
        newUSER.save()

        if newUSER.gender == "male":
            newUSER.profile_pic = "our/pics/" + maleList[m][:-4]+ ".png"
            m+=1

        else:
            newUSER.profile_pic = "our/pics/" + femList[f][:-4]+ ".png"
            f+=1


        newUSER.save()
        num += 1



def getDicttOfGenderPics():
    import os

    directory_in_str = settings.STATIC_ROOT + "/our/pics"

    directory = os.fsencode(directory_in_str)
    maleList = []
    femaleList = []

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".txt"):
            f = open(settings.STATIC_ROOT + "/our/pics/" + filename, "r")
            age = f.readline().split(":")[1]
            gender = f.readline().split(":")[1]

            if gender.__contains__("Female"):
                femaleList.append(filename)
            else:
                maleList.append(filename)
            f.close()
            continue
        else:
            continue
    return {"male": maleList, "female": femaleList}


@transaction.atomic
def makeCourseOBJs():
    allSystemUsers= SystemUser.objects.all()
    allSchoolYears= SchoolYear.objects.all()
    allTeachers= list(SystemUser.objects.filter(role__role="Professor"))

    schoolyearOBJ_17_18= SchoolYear.objects.get(begin=2017)
    
   
   #-----------------  minors  -----------------
    minors= [(0, "Minor em Biologia"), (1, "Minor em Gestão")]
    minorsOBJ= []
    for (_, minor) in minors:
        newCourse= Course(name=minor, grau="Minor", credits_number=30, credits_numberByYear="", duration=2, timetable="Diurno", coordinator=allTeachers.pop())
        newCourse.save()
        minorsOBJ.append(newCourse)


    #-----------------  formaçao e optativas  -----------------
    newCourseF= Course(name="450_Formação Cultural Social e Ética", grau="Formação", timetable="Diurno")
    newCourseF.save()


    newCourseOEI= Course(name="462_Lic. em Eng. Informática ", grau="Optativas", timetable="Diurno")
    newCourseOEI.save()


    newCourseOTI= Course(name="517_Lic. em TIC/TI", grau="Optativas", timetable="Diurno", )
    newCourseOTI.save()


    #-----------------  licenciaturas  -----------------
    newCourseTI= Course(name="Licenciatura em Tecnologias de Informação", grau="Licenciatura", credits_number=180, credits_numberByYear="1:60|2:60|3:60", duration=6, timetable="Diurno", coordinator=allTeachers.pop())
    newCourseTI.save()

    newCourseEI= Course(name="Licenciatura em Engenharia Informática", grau="Licenciatura", credits_number=180, credits_numberByYear="1:60|2:60|3:60", duration=6, timetable="Diurno", coordinator=allTeachers.pop())
    newCourseEI.save()


    #-----------------  couso mini_cursos associaçoes  -----------------
    newCourse_MiniCourse= Course_MiniCourse(course=newCourseEI , miniCourse=newCourseF , credits_number=3, year=2, semestres="2")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseEI , miniCourse=newCourseF , credits_number=3, year=1, semestres="1")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseEI , miniCourse=newCourseOEI , credits_number=6, year=3, semestres="2")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseTI , miniCourse=newCourseF , credits_number=9, year=1, semestres="1")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseTI , miniCourse=minorsOBJ[0] , credits_number=30, year=3, semestres="1,2")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseTI , miniCourse=minorsOBJ[1] , credits_number=30, year=3, semestres="1,2")
    newCourse_MiniCourse.save()

    newCourse_MiniCourse= Course_MiniCourse(course=newCourseTI , miniCourse=newCourseOTI , credits_number=6, year=3, semestres="1,2")
    newCourse_MiniCourse.save()


     


@transaction.atomic
def makeSubjectAndCourseSubjectOBJs():
    with open(settings.MIGRATIONS_DATA_ROOT + "/subjectsData.txt", encoding="utf8") as rfile:
        for line in rfile.readlines():
            if "#" not in line and "||" in line: 
                
                cadeira_curso= line.split("||")
                nomeCadeira, cred = cadeira_curso[0].split(",")
                #print(nomeCadeira)
                newSubject= Subject(name=nomeCadeira, credits_number=int(cred))
                newSubject.save()

                lstCourses= cadeira_curso[1].split("!!")
                for course in lstCourses :
                    nameCourse, year, semester, type = course.split(",")
                    cleanType= type.split("\n")[0] #pq ao usar readlines() o line fica com "\n" no final
                    course= Course.objects.get(name=nameCourse)
                    newCourseSubject= CourseSubject(course=course, subject=newSubject, year=year, semester=semester, type=cleanType)
                    newCourseSubject.save()
                    #print(newCourseSubject)
                    #print(nameCourse)
                    #print(nomeCadeira)
                    #courseSubjectObj= CourseSubject.objects.get(course=course, subject=newSubject)





@transaction.atomic
def makeSystemUserCourseOBJs():
    #allSystemUsers= SystemUser.objects.exclude(id__in= table2.objects.filter(roles=["Admin"]).values_list('id', flat=True))
    allStudents= SystemUser.objects.filter(role__role="Aluno")
    allLicenciaturas= Course.objects.filter(grau="Licenciatura")
    casosPossiveis= [["2016/2017", "1"], ["2016/2017", "2"], ["2016/2017", "3"], ["2017/2018", "1"], ["2017/2018", "2"], ["2018/2019", "1"]]
    for user in allStudents :
        anoInicio, anoAtual= random.choice(casosPossiveis)
        course= random.choice(allLicenciaturas)
        newSystemUserCourse= SystemUserCourse(user=user, course=course, estadoActual="Matriculado", anoLectivoDeInício=anoInicio, anoActual=int(anoAtual))
        if course.name == "Licenciatura em Engenharia Informática":
            newSystemUserCourse.minor= "Nao incluido"
        newSystemUserCourse.save()



@transaction.atomic         
def makeSystemUserSubjectAndLessonSystemUserOBJs():
    with open(settings.MIGRATIONS_DATA_ROOT + "/userSubjectsLessonsData.txt", encoding="utf8") as rfile:
        for line in rfile.readlines():
            if "SystemUserCourse" in line:
                algoritmo= "SystemUserCourse"
            elif "SystemUserSubject" in line :
                algoritmo= "SystemUserSubject"
            
            else:
                if "#" not in line and "," in line: 
                    line= line[:-1] #remover o '\n' do final
                    #se nao for um comentario nem uma linha vazia
                    print(algoritmo)
                    if algoritmo == "SystemUserCourse":
                        #Licenciatura em Tecnologias de Informação,Matriculado,2016/2017,1
                        nameCourse, estado, anoLetivoInicio, ano = line.split(",")
                        CourseObj= Course.objects.get(name=nameCourse)
                        lstSystemUserCourseObj= SystemUserCourse.objects.filter(course=CourseObj, estadoActual=estado, anoLectivoDeInício=anoLetivoInicio, anoActual=ano)

                    else :
                        #ex:1sem++Produção de Documentos Técnicos,1,15.0,TP13!!Curso de Competências Sociais e Desenvolvimento Pessoal,1,18.3,TP11!!Programação I (LTI),1,12.2,T11,TP13,PL13|  |2sem++Introdução às Tecnologias Web,1,14.1,T21,TP21,PL21!!Programação II (LTI),1,13.7,T21,TP21,PL21     
                        for SystemUserCourseObj in lstSystemUserCourseObj:
                            sysUser= SystemUserCourseObj.user
                            somaCredUser= 0

                            #---------- LessonSystemUser objects ----------
                            if anoLetivoInicio == "2016/2017" :
                                    opcoes= "2016/2017||2017/2018"
                            else: # anoLetivoInicio == "2017/2018" :
                                    opcoes= "2017/2018"
                            
                            #-----------------------------------
                            for semSubjLessons in line.split("|  |") :
                                #para cada semestre
                                semestre, subjLessons= semSubjLessons.split("++")
                                for subjLesson in subjLessons.split("!!"):
                                    #para cada cadeira desse semestre
                                    subjName, state, grade, *lstTypeTurma =subjLesson.split(",")
                                    #print(subjName)
                                    SubjObj= Subject.objects.get(name=subjName) 
                                    somaCredUser = somaCredUser + SubjObj.credits_number
                                    turmas_str=  " ".join(lstTypeTurma)
                                    
                                    #---------- LessonSystemUser objects ----------
                                    anoLetivoAprov= random.choice(opcoes.split("||")) #ano letivo em q foi aprovado a cadeira

                                    schoolYearObj= SchoolYear.objects.get(begin=int(anoLetivoAprov.split("/")[0]))
                                    newSystemUserSubject = SystemUserSubject(user= sysUser, subject=SubjObj, state=state, grade=grade, turmas=turmas_str, anoLetivo=schoolYearObj)
                                    newSystemUserSubject.save()

                                    #lstTypeTurma: ["T11","TP13","PL13"]
                                    for typeTurma in lstTypeTurma : 
                                        type, turma= separateLettersNumb(typeTurma)
                                        lessonObjs= Lesson.objects.filter(subject=SubjObj, type=type, turma=turma)
                                        diasDaSemana= ""
                                        for lessonObj in lessonObjs : #ex: T11 terça, T11 quinta
                                            diasDaSemana = lessonObj.week_day

                                            allCorrectDates= lessonSystemUser(anoLetivoAprov, semestre, diasDaSemana)
                                            presDate_str= presenca_in_date(allCorrectDates)

                                            for presData in presDate_str.split("!!") :
                                                presenca, date_str = presData.split(",")
                                                #print(presData)
                                                dataFormat= datetime.strptime(date_str, "%d/%m/%Y").date()
                                                newLessonSystemUser = LessonSystemUser(systemUser=sysUser, lesson=lessonObj, presente=ast.literal_eval(presenca), date=dataFormat)
                                                newLessonSystemUser.save()

                            if SystemUserCourseObj.minor != "Nao incluido":
                                #lti
                                courseDoUser= SystemUserCourseObj.course
                                C_miniCursos= Course_MiniCourse.objects.filter(course=courseDoUser)
                                minors= [] #get todos os minors daquele curso
                                for C_miniCurso in C_miniCursos:
                                    if C_miniCurso.miniCourse.grau == "Minor" :
                                        minors.append(C_miniCurso.miniCourse)

                                if somaCredUser >= 108 :
                                    minorEscolhido= random.choice(minors)
                                    SystemUserCourseObj.minor= minorEscolhido.name

                            SystemUserCourseObj.totalCred= somaCredUser
                            SystemUserCourseObj.save()




# -- variaveis --
dic = {  "2016/2017": {'1sem': ["20/09/2016", "21/12/2016"], '2sem': ["20/02/2017", "31/05/2017"]},  
         "2017/2018": {'1sem': ["18/09/2017", "21/12/2017"], '2sem': ["19/02/2018", "30/05/2018"]}}

lstDiasDaSemana= ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
feriados= ['01/11/2016', '01/12/2016', '08/12/2016'] #incompleto
ferias= [["04/03", "06/03"], #carnaval
         ["17/04", "23/04"]] #pascoa


def lessonSystemUser(anoLetivoAprov, semestre, diasDaSemana):
    dataInicio, dataFinal= dic[anoLetivoAprov][semestre]
    ano= dataInicio.split("/")[2]
    joinFerias= allFeriasDate(ferias, ano)
    joinFeriasAndFeriados= joinFerias + feriados
    return getDatesBetween2Dates(dataInicio, dataFinal, joinFeriasAndFeriados, diasDaSemana)


def getDatesBetween2Dates(dataInicio, dataFinal, lazyDays=None, diasDaSemana=lstDiasDaSemana):
  """
  devolve todas as datas que calham em dias de semana especificos
  lazyDays != none, retira as datas q sejam feriados ou no periodo de mini ferias
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
  #ex: [['04/03/2018', '06/03/2018'], ['17/04/2018', '23/04/2018']]
  return list(map(lambda lst: list(map(lambda dm: dm + "/" + ano, lst)), ferias))


def allFeriasDate(ferias, ano):
  #ex: ['04/03/2018', '05/03/2018', '06/03/2018', '17/04/2018', '18/04/2018', ... , '23/04/2018']
  newFerias= convertFerias(ferias, ano)
  newFerias_str= []
  for f in newFerias:
    dataInicio, dataFinal= f
    newFerias_str = newFerias_str + getDatesBetween2Dates(dataInicio, dataFinal)
  return newFerias_str


def presenca_in_date(allCorrectDates) :
  bool= ["True", "False"]
  prob= [0.85,0.15]

  prim= True
  for date in allCorrectDates:
    ispresent= random.choices(bool, prob)[0]
    if prim :
      output = ispresent + "," + date
      prim= False
    else:
      output = output + "!!" + ispresent + "," + date

  return output


def separateLettersNumb(string):
    #"TP13" fica ['TP', '13']
    return re.split('(\d+)',string)[:-1]



@transaction.atomic         
def makeLessonOBJs():
    with open(settings.MIGRATIONS_DATA_ROOT + "/lessonsData.txt", encoding="utf8") as rfile:
        for line in rfile.readlines():
            if "#" not in line and "||" in line: 
                
                cadeira_lessons= line.split("||")
                nomeCadeira = cadeira_lessons[0]
                #print(nomeCadeira)
                lstLessons= cadeira_lessons[1].split("!!")

                for lesson in lstLessons :
                    type, turma, weekDay, hour, duration = lesson.split(",")
                    if len(hour) == 4 : 
                        hour= "0" + hour
                    if len(turma) == 1 :
                        turma= "0" + turma
                    cleanDuration= duration.split("\n")[0] #pq ao usar readlines() o line fica com "\n" no final
                    subject= Subject.objects.get(name=nomeCadeira)
                    newLesson= Lesson(subject=subject, type=type, turma=turma, week_day=weekDay, hour=hour, duration=cleanDuration)
                    newLesson.save()
    
    #put rooms
    lessons= Lesson.objects.order_by("week_day", "subject__name", "turma")
    rooms= Room.objects.filter(can_give_class= True) #200 rooms that can have class
    prim=True
    i=0

    for lesson in lessons:
        if prim :
            lesson.room=rooms[i]
            prim = False
        else :
            if lessonAnt.week_day != lesson.week_day :
                i= 0
                lesson.room=rooms[i]
            else: #no mesmo dia de semana
                if addMinutes(lessonAnt.hour, lessonAnt.duration) <= hourToMinutes(lesson.hour) :
                    lesson.room=rooms[i]
                else: 
                    i = (i+1) % rooms.count() #array circular
                    lesson.room=rooms[i]
        lesson.save()
        lessonAnt = lesson



    #atribuir professores
    lstLessonsPrim= []
    lstLessonsSeg= []

    #dados
    subjs= Subject.objects.all()
    allTeachers= SystemUser.objects.filter(role__role="Professor")

    #separar cadeiras por semestre e ordena-las
    for subj in subjs:
        lesson= Lesson.objects.filter(subject=subj).order_by("week_day", "hour") #lista de lessons
        CRsubjs= CourseSubject.objects.filter(subject=subj)
        if CRsubjs[0].semester == 1 :
            lstLessonsPrim.append(lesson)
        else: #2
            lstLessonsSeg.append(lesson)

    allLessons = [lstLessonsPrim, lstLessonsSeg]
   
 
    for semestre in allLessons:
        i = 0
        for lessons in semestre: #lessons- lista de lessons de todas as cadeiras de um semestre
            subjectProfs= []
            for lesson in lessons: #lessons de uma cadeira

                while is_lesson_sobreposta(allTeachers[i], lesson):
                    i = (i+1) % allTeachers.count() #array circular
                
                lesson.professor= allTeachers[i]
                lesson.save()
                subjectProfs.append(lesson.professor)

            #todos os professores dessa cadeira
            TuplosProfNumOrd = ordenarPorNumOcorrencias(subjectProfs) #sort: professor q da mais aulas dessa cadeira
            subj= lesson.subject
            tem= False
            for prof,n in TuplosProfNumOrd:
                if not Subject.objects.filter(regente=prof).first() : #este prof ainda nao é regente
                    subj.regente =  prof
                    tem= True
                    break
            if not tem :
                subj.regente = TuplosProfNumOrd[0][0] #nota: assim um prof pode ser regente de mais uma cadeira!
            subj.save()


def is_lesson_sobreposta(professor, lesson):
    lessonProfAnt= Lesson.objects.filter(professor=professor, week_day=lesson.week_day).order_by("hour").last()
    if lessonProfAnt : #se ele ja tiver aulas nesse dia de semana
        if addMinutes(lessonProfAnt.hour, lessonProfAnt.duration) <= hourToMinutes(lesson.hour) :
            return False
        else:
            return True
        
    return False



def ordenarPorNumOcorrencias(lstObjs):
    counts = collections.Counter(lstObjs)
    tuploOrd= counts.most_common(len(counts))
    return tuploOrd


def hourToMinutes(hour):
    lhour= hour.split(":")
    return int(lhour[0])*60 + int(lhour[1])


def addMinutes(hour, duration):
    return hourToMinutes(hour) + hourToMinutes(duration)



def mainInsertData(apps, schema_editor):
    #reset (para nao dar duplicado)
    Role.objects.all().delete()
    SchoolYear.objects.all().delete()
    Room.objects.all().delete()
    SystemUser.objects.all().delete()
    PersonalInfo.objects.all().delete()
    Course.objects.all().delete()
    Subject.objects.all().delete()
    CourseSubject.objects.all().delete()
    SystemUserCourse.objects.all().delete() 
    Lesson.objects.all().delete()
    SystemUserSubject.objects.all().delete()
    LessonSystemUser.objects.all().delete()

    makeRoleOBJs()
    makeSchoolYearOBJs(2016,2019)
    makeRoomOBJs(200,42)
    makeSystemUserOBJs()
    makePersonalInfoOBJs()
    makeCourseOBJs()
    makeSubjectAndCourseSubjectOBJs()
    makeSystemUserCourseOBJs() #falta
    makeLessonOBJs()
    makeSystemUserSubjectAndLessonSystemUserOBJs() #falta



class Migration(migrations.Migration):
    dependencies = [
        ('university', '0002_insertDataUsers'),
    ]
    
    operations = [
        migrations.RunPython(mainInsertData)
    ]








