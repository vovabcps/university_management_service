from django.db import models
from django.conf import settings






STUDENT_ROLE = 'Aluno'
TEACHER_ROLE = 'Professor'
ADMIN_ROLE = 'Admin'


class SchoolYear(models.Model):
    begin = models.IntegerField(unique=True)
    end = models.IntegerField(unique=True)



class Room(models.Model):
    room_number = models.CharField(max_length=200, unique=True)
    can_give_class = models.BooleanField()


class Role(models.Model):
    role = models.CharField(max_length=200,  unique=True)


    def is_a(self, role_char):
            return self.role == role_char

#1 aluno pode pertece a mais que uma faculdade (so se for minor)

class SystemUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, null=True,  on_delete=models.CASCADE)
    rooms = models.ManyToManyField(Room) #gabinete

    def get_roles(self):
        return self.role.role

    def gabinete(self):
        return ",\n".join([room.room_number for room in self.rooms.all()])


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
    credits_number = models.IntegerField(null=True)
    duration= models.IntegerField(null=True) #semesters
    timetable= models.CharField(max_length=200, null=True) #Diurno
    coordinator = models.OneToOneField(SystemUser, on_delete=models.SET_NULL, null=True)
     #o coordenador é um professor qualquer, nao precisa de dar nenhuma aula das cadeiras desse curso

    def get_coordinator_name(self):
        detalhesOBJ= PersonalInfo.objects.get(user=self.coordinator)
        return detalhesOBJ.name


class Course_MiniCourse(models.Model):
    course= models.ForeignKey(Course, on_delete=models.CASCADE)
    miniCourse= models.ForeignKey(Course, related_name="miniCourso", on_delete=models.CASCADE)
    credits_number = models.IntegerField(null=True)
    year= models.IntegerField(default=0) #1,2,3,4..
    semester = models.IntegerField(default=0) #em q semestre começa, semester + Course duration , 

    #pq ha mini cursos em que os seus credits_number variam de semestre para semeste(exemplo minor), 
    #por isso so posso ter uma linnha nesta tabela com o total de credits_number
    #ex: (Licenciatura em Tecnologias de Informação, Minor em Biologia, 30, 3, 1)
    #começa no 1º semestre e dura 2 semestres
    
    #ex: (Licenciatura em Engenharia Informática, 450_Formação Cultural Social e Ética - FCSE, 3, 2, 2)
    #ex: (Licenciatura em Engenharia Informática, 450_Formação Cultural Social e Ética - FCSE, 3, 1, 1)

    #ex: (Licenciatura em Tecnologias de Informação, 450_Formação Cultural Social e Ética - FCSE, 9, 1, 1)

    def get_course_name(self):
        return self.course.name

    def get_miniCourse_name(self):
        return self.miniCourse.name


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

    def get_systemUser_user(self):
        return self.user.user #ex: fc1085

    def get_course_name(self):
        return self.course.name

class SystemUser_SchoolYear(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    


class Subject(models.Model):
    #id -> codigo
    name = models.CharField(max_length=200, unique=True)
    credits_number = models.IntegerField(default=6) 
    regente = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True)  #o regente da cadeira tem q dar aulas dessa cadeira

    def get_regente_name(self):
        detalhesOBJ= PersonalInfo.objects.get(user=self.regente)
        return detalhesOBJ.name
        #return self.regente.user

    class Meta:
        ordering = ['name']



class CourseSubject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year= models.IntegerField(default=0) #1,2,3,4..
    semester = models.IntegerField(default=0) # 1 or 2 
    type= models.CharField(max_length=200, null=False, default="Semestral") #Semestral, Semestral (Opção), Anual

    def get_course_name(self):
        return self.course.name

    def get_subject_name(self):
        return self.subject.name 

    def get_subject_credits(self):
        return self.subject.credits_number 


class SystemUserSubject(models.Model):
    user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # 0 - pending, 1 - approved, 2 - not approved
    state = models.IntegerField(null=True)
    grade = models.FloatField(null=True)

    def get_systemUser_user(self):
        return self.user.user #ex: fc1085

    def get_subject_name(self):
        return self.subject.name 




class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # T, TP, PL, O ...
    type = models.CharField(max_length=200, null=False, default="T")
    turma = models.CharField(max_length=200, null=False, default="")
    week_day = models.CharField(max_length=200, null=True)
    hour = models.CharField(max_length=200, null=True)
    duration = models.CharField(max_length=200, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    professor = models.ForeignKey(SystemUser, on_delete=models.CASCADE, null=True)
    presencas = models.IntegerField(null=True)


    def get_lesson_detalhes(self):
        return self.subject.name  + ", " + self.type + ", " + self.week_day + ", " + self.hour

    def get_subject_name(self):
        return self.subject.name 

    def professor_fc(self):
        return self.professor.user 

    def room_number(self):
        return self.room.room_number     

    def __str__(self):
        return self.subject.name

    class Meta:
        ordering = ['subject__name']




class LessonSystemUser(models.Model):
    lesson= models.ForeignKey(Lesson, on_delete=models.CASCADE)
    systemUser= models.ForeignKey(SystemUser, on_delete=models.CASCADE) #so alunos xd
    presente= models.BooleanField()
    date= models.DateField()


    def get_systemUser_user(self):
        return self.systemUser.user #ex: fc1085

    def get_lesson_information(self):
        return self.lesson.get_lesson_detalhes(self)



