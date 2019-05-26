from django.contrib import admin
from .models import *



class SchoolYearAdmin(admin.ModelAdmin):
  search_fields = ["begin", "end"]
  list_display = ["id", "begin", "end"]
admin.site.register(SchoolYear, SchoolYearAdmin)


class RoomAdmin(admin.ModelAdmin):
  search_fields = ["room_number"]
  list_filter = ["can_give_class"]
  list_display = ["id", "room_number","can_give_class"]
admin.site.register(Room, RoomAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "role"]
admin.site.register(Role, RoleAdmin)


class SystemUserAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_filter = ["role__role"]
    list_display = ["id", "user", "get_roles", "gabinete"]
admin.site.register(SystemUser, SystemUserAdmin)


class PersonalInfoAdmin(admin.ModelAdmin):
    search_fields = ["user__user__username", "personal_email", "name", "id_document", "vat_number"]
    list_filter = ["gender", "nationality"]
    list_display = ["id", "get_systemUser_user", "name" , "personal_email", "gender", "nationality", "birth_date", "vat_number"]
admin.site.register(PersonalInfo, PersonalInfoAdmin)


class CourseAdmin(admin.ModelAdmin):
  search_fields = ["name"]
  list_filter = ["grau", "credits_number", "duration", "timetable"]
  list_display = ["id", "name", "grau", "credits_number", "duration", "get_coordinator_name", "timetable"]
admin.site.register(Course, CourseAdmin)

class Course_MiniCourseAdmin(admin.ModelAdmin):
  search_fields = ["course__name", "miniCourse__name"]
  list_filter = ["credits_number", "year", "semestres"]
  list_display = ["id", "get_course_name", "get_miniCourse_name", "credits_number", "year", "semestres"]
admin.site.register(Course_MiniCourse,  Course_MiniCourseAdmin)


class SystemUserCourseAdmin(admin.ModelAdmin):
  search_fields = ["user__user__username"]
  list_filter = ["estadoActual", "anoLectivoDeInício", "anoActual"]
  list_display = ["id", "get_systemUser_user", "get_course_name", "estadoActual", "anoLectivoDeInício", "anoActual"]
admin.site.register(SystemUserCourse,  SystemUserCourseAdmin)


class SubjectAdmin(admin.ModelAdmin):
  search_fields = ["name"]
  list_filter = ["credits_number"]
  list_display = ["id", "name", "credits_number", "get_regente_name"]
admin.site.register(Subject,  SubjectAdmin)


class CourseSubjectAdmin(admin.ModelAdmin):
  search_fields = ["course__name", "subject__name"]
  list_filter = ["year", "semester", "type"]
  list_display = ["id", "get_course_name", "get_subject_name", "year", "semester", "type"]
admin.site.register(CourseSubject,  CourseSubjectAdmin)

class SystemUserSubjectAdmin(admin.ModelAdmin):
  search_fields = ["user__user__username", "grade"]
  list_filter = ["subject__name", "state"]
  list_display = ["id", "get_systemUser_user", "get_subject_name", "state", "grade"]
admin.site.register(SystemUserSubject,  SystemUserSubjectAdmin)

class LessonAdmin(admin.ModelAdmin):
  search_fields = ["subject__name", "professor__user__username", "room__room_number", "turma"]
  list_filter = ["type", "week_day", "hour", "duration", "presencas"]
  list_display = ["id", "get_subject_name", "type", "turma", "week_day", "hour", "duration", "professor_fc", "room_number", "presencas"]
admin.site.register(Lesson,  LessonAdmin)

class LessonSystemUserAdmin(admin.ModelAdmin):
  search_fields = ["user__user__username", "date"]
  list_filter = ["presente"]
  list_display = ["id", "get_lesson_information", "get_systemUser_user", "presente", "date"]
admin.site.register(LessonSystemUser,  LessonSystemUserAdmin)



"""
class __bla__Admin(admin.ModelAdmin):
  search_fields = []
  list_filter = []
  list_display = []
admin.site.register(__bla__,  __bla__Admin)
"""