from django.db import migrations, transaction
from ..models import *
from django.conf import settings
import math
import random
from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import get_object_or_404







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
    roles = ["Professor", "Aluno", "Admin", "Monitor", "Aluno externo", "Erasmus"]
    for r in roles:
        newRole= Role(role=r)
        newRole.save()



@transaction.atomic
def makeSystemUserOBJs():
    #800 users
    #42 gabinetes
    allUsers= User.objects.all()
    gabinetes= Room.objects.filter(can_give_class= False)
    #roles objs
    rProfessor= Role.objects.get(role="Professor")
    rAluno= Role.objects.get(role="Aluno")
    rAdmin= Role.objects.get(role="Admin")
    rMonitor= Role.objects.get(role="Monitor")
    rAlunoExterno= Role.objects.get(role="Aluno externo")
    rErasmus= Role.objects.get(role="Erasmus")

    #[totalusers , [roles], tem gabinete?]
    #totalUserRoles= [ [3, [rAdmin], True], [1, [rAdmin, rAluno], True], [10, [rAlunoExterno], False], [2, [rErasmus], False], 
    #                  [3, [rMonitor], False], [84, [rProfessor], True], [1, [rAluno, rAlunoExterno], False], [800, [rAluno], False] ] #-1 -> o resto

    totalUserRoles= [ [3, rAdmin, True], [1, rAdmin, True], [10, rAlunoExterno, False], [2, rErasmus, False], 
                   [3, rMonitor, False], [84, rProfessor, True], [1, rAluno, False], [800, rAluno, False] ] #-1 -> o resto

    #4 gabinetes vao ter 3 pessoas cada, e o resto(32) vao ter 2 pessoas cada

    cont=1
    i=0
    gab= 0
    for user in allUsers :
        total= sum([n for (n,l,b) in totalUserRoles[:(i+1)]]) 
        if cont > total :
            i += 1
        newUSER= SystemUser(user=user, role=totalUserRoles[i][1])
        newUSER.save()
        #newUSER.roles.add(* totalUserRoles[i][1]) 

        if totalUserRoles[i][2] :
            newUSER.rooms.add(gabinetes[gab])
            gab = (gab+1) % gabinetes.count() #array circular
        cont += 1 



@transaction.atomic
def makePersonalInfoOBJs():
    allSystemUsers= SystemUser.objects.all()
    with open(settings.STATIC_ROOT + "/NamesGenderNationalityBirthAdressVat800.txt") as rfile:
        listData = rfile.readlines()
    num= 0
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
        num += 1


@transaction.atomic
def makeCourseOBJs():
    allSystemUsers= SystemUser.objects.all()
    allSchoolYears= SchoolYear.objects.all()
    allTeachers= list(SystemUser.objects.filter(role__role="Professor"))
    #allTeachers= list(SystemUser.objects.filter(roles__role="Professor"))

    schoolyearOBJ_17_18= SchoolYear.objects.get(begin=2017)
    
    #minors
    minors= [(0, "Minor em Biologia"), (1, "Minor em Estatística e Investigação Operacional"), (2, "Minor em Física"), 
    (3, "Minor em Geologia"), (4, "Minor em História e Filosofia das Ciências"), (5, "Minor em Informática"), 
    (6, "Minor em Matemática"), (7, "Minor em Química"), (8, "Minor em Tecnologia de Informação Geográfica")]
    

    minorsOBJ= []

    for (_, minor) in minors:
        newCourse= Course(name=minor, grau="Minor", credits_number=30, duration=2, timetable="Diurno", coordinator=allTeachers.pop())
        newCourse.save()
        minorsOBJ.append(newCourse)

    newCourse= Course(name="Licenciatura em Tecnologias de Informação", grau="Licenciatura", credits_number=180, duration=6, timetable="Diurno", coordinator=allTeachers.pop())
    newCourse.save()
    newCourse.minors_ramos.add(*[minorsOBJ[0], minorsOBJ[1], minorsOBJ[8]])

def makeSubjectAndCourseSubjectOBJs():
    with open(settings.STATIC_ROOT + "/subjectsData.txt") as rfile:
        for line in rfile.readlines():
            if "#" not in line and "||" in line: 
                
                cadeira_curso= line.split("||")
                nomeCadeira, cred = cadeira_curso[0].split(",")
                newSubject= Subject(name=nomeCadeira, credits_number=int(cred))
                newSubject.save()

                lstCourses= cadeira_curso[1].split("!!")
                for course in lstCourses :
                    nameCourse, year, semester, type = course.split(",")
                    course= Course.objects.get(name=nameCourse)
                    newCourseSubject= CourseSubject(course=course, subject=newSubject, year=year, semester=semester, type=type)
                    newCourseSubject.save()






def makeSystemUserCourseOBJs():
    #allSystemUsers= SystemUser.objects.exclude(id__in= table2.objects.filter(roles=["Admin"]).values_list('id', flat=True))
    allSystemUsers= SystemUser.objects.all()
    allCourses= Course.objects.all()

    allMinors= Course.objects.filter(grau="Minor")
    allLicenciaturas= Course.objects.filter(grau="Licenciatura")
    for user in allSystemUsers :
        roles_str= user.get_roles()
        #if "Admin" not in roles_str and "Erasmus" not in roles_str and "Professor" not in roles_str:
        if "Admin" != roles_str and "Erasmus" != roles_str and "Professor" != roles_str:
            if "Aluno externo" == roles_str : #if "Aluno externo" in roles_str :
                SystemUserCourse(user=user, course=random.choice(allMinors), estadoActual="Matriculado", anoLectivoDeInício="2017/2018", anoActual=2)
            
            if "Monitor" == roles_str : #if "Monitor" in roles_str :
                SystemUserCourse(user=user, course=random.choice(allLicenciaturas), estadoActual="Matriculado", anoLectivoDeInício="2017/2018", anoActual=2)
            
            if "Aluno" == roles_str : #if "Aluno" in roles_str :
                SystemUserCourse(user=user, course=random.choice(allLicenciaturas), estadoActual="Matriculado", anoLectivoDeInício="2017/2018", anoActual=2)
            

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

    makeRoleOBJs()
    makeSchoolYearOBJs(2017,2019)
    makeRoomOBJs(200,42)
    makeSystemUserOBJs()
    makePersonalInfoOBJs()
    makeCourseOBJs()
    makeSubjectAndCourseSubjectOBJs()
    makeSystemUserCourseOBJs()

class Migration(migrations.Migration):
    dependencies = [
        ('university', '0002_insertDataUsers'),
    ]
    
    operations = [
        migrations.RunPython(mainInsertData)
    ]








