from django.contrib import admin
from .models import *



class SchoolYearAdmin(admin.ModelAdmin):
  search_fields = ["begin", "end"]
  list_display = ["begin", "end"]
admin.site.register(SchoolYear, SchoolYearAdmin)


class RoomAdmin(admin.ModelAdmin):
  search_fields = ["room_number"]
  list_filter = ["can_give_class"]
  list_display = ["room_number","can_give_class"]
admin.site.register(Room, RoomAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ["role"]
admin.site.register(Role, RoleAdmin)


class SystemUserAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_filter = ["role__role"]
    list_display = ["user", "get_roles", "get_rooms"]
admin.site.register(SystemUser, SystemUserAdmin)


class PersonalInfoAdmin(admin.ModelAdmin):
    search_fields = ["user__user__username", "personal_email", "name", "id_document", "vat_number"]
    list_filter = ["gender", "nationality"]
    list_display = [ "get_systemUser_user", "name" , "personal_email", "gender", "nationality", "birth_date", "vat_number"]
admin.site.register(PersonalInfo, PersonalInfoAdmin)


class CourseAdmin(admin.ModelAdmin):
  search_fields = ["name"]
  list_filter = ["grau", "credits_number", "duration", "timetable"]
  list_display = ["name", "grau", "credits_number", "duration", "get_coordinator_name", "timetable"]
admin.site.register(Course, CourseAdmin)

class Course_MiniCourseAdmin(admin.ModelAdmin):
  search_fields = ["course__name", "miniCourse__name"]
  list_filter = ["credits_number", "year", "semester"]
  list_display = ["get_course_name", "get_miniCourse_name", "credits_number", "year", "semester"]
admin.site.register(Course_MiniCourse,  Course_MiniCourseAdmin)


class SystemUserCourseAdmin(admin.ModelAdmin):
  search_fields = ["user__user__username"]
  list_filter = ["estadoActual", "anoLectivoDeInício", "anoActual"]
  list_display = ["get_systemUser_user", "get_course_name", "estadoActual", "anoLectivoDeInício", "anoActual"]
admin.site.register(SystemUserCourse,  SystemUserCourseAdmin)


class SubjectAdmin(admin.ModelAdmin):
  search_fields = ["name"]
  list_filter = ["credits_number"]
  list_display = ["name", "credits_number", "get_regente_name"]
admin.site.register(Subject,  SubjectAdmin)


class CourseSubjectAdmin(admin.ModelAdmin):
  search_fields = ["course__name", "subject__name"]
  list_filter = ["year", "semester", "type"]
  list_display = ["get_course_name", "get_subject_name", "year", "semester", "type"]
admin.site.register(CourseSubject,  CourseSubjectAdmin)

class SystemUserSubjectAdmin(admin.ModelAdmin):
  search_fields = ["user__user__username", "grade"]
  list_filter = ["subject__name", "state"]
  list_display = ["get_systemUser_user", "get_subject_name", "state", "grade"]
admin.site.register(SystemUserSubject,  SystemUserSubjectAdmin)

class LessonAdmin(admin.ModelAdmin):
  search_fields = ["subject"]
  list_filter = ["type", "week_day", "hour", "duration", "room", "presenças"]
  list_display = ["get_subject_name", "type", "week_day", "hour", "duration", "get_room_room_number", "presenças"]
admin.site.register(Lesson,  LessonAdmin)





"""
class __bla__Admin(admin.ModelAdmin):
  search_fields = []
  list_filter = []
  list_display = []
admin.site.register(__bla__,  __bla__Admin)
"""