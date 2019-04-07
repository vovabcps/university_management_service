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
    list_filter = ["roles__role"]
    list_display = ["user", "get_roles", "get_rooms"]
admin.site.register(SystemUser, SystemUserAdmin)


class PersonalInfoAdmin(admin.ModelAdmin):
    search_fields = ["user__user__username", "personal_email", "name", "id_document", "vat_number"]
    list_filter = ["gender", "nationality"]
    list_display = [ "get_systemUser_user", "name" , "personal_email", "gender", "nationality", "birth_date", "vat_number"]
admin.site.register(PersonalInfo, PersonalInfoAdmin)


admin.site.register(Course)


admin.site.register(SystemUserCourse)
admin.site.register(Subject)
admin.site.register(CourseSubject)
admin.site.register(SystemUserSubject)
admin.site.register(Lesson)