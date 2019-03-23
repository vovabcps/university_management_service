from django.db import models
from django.conf import settings


class SchoolYear(models.Model):
    begin = models.IntegerField()
    end = models.IntegerField()


class Room(models.Model):
    room_number = models.CharField(max_length=200, )
    can_give_class = models.BooleanField()


class Role(models.Model):
    role = models.CharField(max_length=200 )


class SystemUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    rooms = models.ManyToManyField(Room)


class PersonalInfo(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True)
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=200, null=True)
    personal_email = models.CharField(max_length=200, null=True)
    gender = models.CharField(max_length=200, null=True)
    nationality = models.CharField(max_length=200, null=True)
    id_document = models.CharField(max_length=200, null=True)
    vat_number = models.CharField(max_length=200, null=True)


class Course(models.Model):
    name = models.CharField(max_length=200)
    credits_number = models.FloatField()
    coordinator = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)


class SystemUserCourse(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester1 = models.IntegerField(null=True)
    semester2 = models.IntegerField(null=True)


class Subject(models.Model):
    name = models.CharField(max_length=200, )
    credits = models.FloatField()
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    coordinator = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True)
    # 1 or 2
    half = models.IntegerField()


class CourseSubject(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()


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
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    users = models.ManyToManyField(SystemUser)
