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
def makeAuth_userOBJs():
    newUSER= User.objects.create_user(username="adminF", password="damabranca", email="adminF@alunos.fc.ul.pt", is_superuser=True, is_staff=True)
    #newUSER= User(username="adminF", password="damabranca", email="adminF@alunos.fc.ul.pt", is_superuser=True, is_staff=True)
    newUSER.save()
    for _ in range(799):
        obj = User.objects.latest('id')
        newUSER= User.objects.create_user(username="fc"+str((obj.id+1)), password="blabla"+str((obj.id+1)), email="fc"+str((obj.id+1))+"@alunos.fc.ul.pt", is_superuser=False)
        #newUSER= User(username="fc"+str((obj.id+1)), password="blabla"+str((obj.id+1)), email="fc"+str((obj.id+1))+"@alunos.fc.ul.pt", is_superuser=False)
        newUSER.save()


@transaction.atomic
def makeSystemUserOBJs():
    allUsers= User.objects.all()
    r= Role.objects.get(role="Aluno")
    for user in allUsers :
        newUSER= SystemUser(user=user) #,rooms= )
        newUSER.save()
        newUSER.roles.add(r)


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


def mainInsertData(apps, schema_editor):
    makeRoleOBJs()
    makeSchoolYearOBJs(2017,2019)
    makeRoomOBJs(200,42)
    makeAuth_userOBJs()
    makeSystemUserOBJs()
    makePersonalInfoOBJs()

class Migration(migrations.Migration):
    dependencies = [
        ('university', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(mainInsertData)
    ]








