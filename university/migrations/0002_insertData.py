from django.db import migrations, transaction
from ..models import *
from django.conf import settings
from django.contrib.auth import get_user_model
import math
from django.contrib.auth.models import User







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
    newUSER= User.objects.create_user(username="adminF", password="damabranca", is_superuser=True, is_staff=True)
    newUSER.save()
    with open(settings.STATIC_ROOT + "/peoplesName800PT.txt") as rfile:
        for line in rfile:
            #[fname, lname] = line.split()
            fname_lname = line.split()
            obj = User.objects.latest('id')
            newUSER= User.objects.create_user(username="fc"+str((obj.id+1)), password=fname_lname[0]+"123", email="fc"+str((obj.id+1))+"@alunos.fc.ul.pt", is_superuser=False, first_name=fname_lname[0], last_name=fname_lname[1])
            newUSER.save()


def mainInsertData(apps, schema_editor):
    makeRoleOBJs()
    makeSchoolYearOBJs(2017,2019)
    makeRoomOBJs(200,42)
    makeAuth_userOBJs()

class Migration(migrations.Migration):
    dependencies = [
        ('university', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(mainInsertData)
    ]








