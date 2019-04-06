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



class SystemUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    rooms = models.ManyToManyField(Room)
#(1, 1, 1)


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
#(2, Rua de Sesamo, 12/12/2012, Rute Monteiro, 933 333 333, hotmail, Female, Portugues, 15155821, nif )


class Course(models.Model):
    name = models.CharField(max_length=200, unique=True)
    credits_number = models.FloatField()
    coordinator = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
#(LTI , 260.0, professor, 2018/2019)


class SystemUserCourse(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester1 = models.IntegerField(null=True)
    semester2 = models.IntegerField(null=True)
#(49050, LTI, 1, 2)


class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    credits = models.FloatField()
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    coordinator = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True)
    # 1 or 2
    half = models.IntegerField(default=0)
#(Aplicações Distribuidas, 6.0, 2018/2019, Jóse Cecilio, ???)


class CourseSubject(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
#(Aplicações Distribuidas, LTI, 1)


class SystemUserSubject(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # 0 - pending, 1 - approved, 2 - not approved
    state = models.IntegerField(null=True)
    grade = models.FloatField(null=True)
#(49050, Aplicações Distribuidas, 2, ?null?)


class Lesson(models.Model):
    # 0 - T, 1 - TP, 2 - PL, 3 - O ...
    type = models.IntegerField()
    week_day = models.IntegerField()
    hour = models.TimeField()
    duration = models.FloatField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    users = models.ManyToManyField(SystemUser)
#(0, 2, 18:45, 1:30, 3.2.15, Aplicações Distribuidas, 2018/2019, 49050)
