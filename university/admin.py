from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SchoolYear)


class RoomAdmin(admin.ModelAdmin):
  search_fields = ["room_number"]
  list_filter = ("can_give_class", "room_number")
  list_display = ("room_number","can_give_class")
admin.site.register(Room, RoomAdmin)

admin.site.register(Role)
admin.site.register(SystemUser)
admin.site.register(PersonalInfo)
admin.site.register(Course)
admin.site.register(SystemUserCourse)
admin.site.register(Subject)
admin.site.register(CourseSubject)
admin.site.register(SystemUserSubject)
admin.site.register(Lesson)