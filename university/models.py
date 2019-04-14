from django.db import models
from django.conf import settings


class SchoolYear(models.Model):
    begin = models.IntegerField(unique=True)
    end = models.IntegerField(unique=True)



class Room(models.Model):
    room_number = models.CharField(max_length=200, unique=True)
    can_give_class = models.BooleanField()


class Role(models.Model):
    role = models.CharField(max_length=200,  unique=True)



#1 aluno pode pertece a mais que uma faculdade (so se for minor)

class SystemUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    rooms = models.ManyToManyField(Room)

    def get_roles(self):
        return "\n".join([r.role for r in self.roles.all()])

    def get_rooms(self):
        return "\n".join([room.room_number for room in self.rooms.all()])


class PersonalInfo(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True)
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=200, null=True)
    personal_email = models.CharField(max_length=200, null=True, unique=True)
    gender = models.CharField(max_length=200, null=True)
    nationality = models.CharField(max_length=200, null=True)
    id_document = models.CharField(max_length=200, null=True, unique=True)
    vat_number = models.CharField(max_length=200, null=True, unique=True)

    def get_systemUser_user(self):
        return self.user.user #ex: fc1085


class Faculdade(models.Model):
    name = models.CharField(max_length=200, default="Faculdade de Ciências")


class Course(models.Model):
    name = models.CharField(max_length=200, unique=True)
    grau = models.CharField(max_length=200, null=False, default="Licenciatura")
    #Licenciatura, Minor, ramos, mestrado
    credits_number = models.IntegerField(default=180)
    duration= models.IntegerField(null=True) #semesters
    timetable= models.CharField(max_length=200, null=True)
    coordinator = models.OneToOneField(SystemUser, on_delete=models.SET_NULL, null=True)
     #o coordenador é um professor qualquer, nao precisa de dar nenhuma aula das cadeiras desse curso
    minors_ramos= models.ManyToManyField("self")


class SystemUser_Faculdade(models.Model): #ex: fazer minor em outra faculdade
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    faculdade= models.ForeignKey(Faculdade, on_delete=models.CASCADE)

class Course_Faculdade(models.Model):
    faculdade= models.ForeignKey(Faculdade, on_delete=models.CASCADE)
    course= models.ForeignKey(Course, on_delete=models.CASCADE)

class Course_SchoolYear(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    course= models.ForeignKey(Course, on_delete=models.CASCADE)

class SystemUserCourse(models.Model):
    #users que estao inscritos em cursos
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    estadoActual = models.CharField(max_length=200, null=True) #ex: matriculado
    anoLectivoDeInício = models.CharField(max_length=200, null=True) #ex: 2016/2017
    anoActual = models.IntegerField(null=True) #1ºano, 2ºano, ...

class SystemUser_SchoolYear(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    


class Subject(models.Model):
    #id -> codigo
    name = models.CharField(max_length=200, unique=True)
    credits_number = models.IntegerField(default=6) 
    regente = models.OneToOneField(SystemUser, on_delete=models.SET_NULL, null=True)  #o regente da cadeira tem q dar aulas dessa cadeira



class CourseSubject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year= models.IntegerField(default=0) #1,2,3,4..
    semester = models.IntegerField(default=0) # 1 or 2 
    type= models.CharField(max_length=200, null=False, default="Semestral") #Semestral, Semestral (Opção), Anual


class SystemUserSubject(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # 0 - pending, 1 - approved, 2 - not approved
    state = models.IntegerField(null=True)
    grade = models.FloatField(null=True)



class Lesson(models.Model):
    # 0 - T, 1 - TP, 2 - PL, 3 - O ...
    type = models.IntegerField()
    week_day = models.IntegerField()
    hour = models.TimeField()
    duration = models.FloatField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    users = models.ManyToManyField(SystemUser)
    presenças= models.IntegerField()


