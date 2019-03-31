from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SchoolYear)
admin.site.register(Room)
admin.site.register(Role)
admin.site.register(SystemUser)
admin.site.register(PersonalInfo)
admin.site.register(Course)
admin.site.register(SystemUserCourse)
admin.site.register(Subject)
admin.site.register(CourseSubject)
admin.site.register(SystemUserSubject)
admin.site.register(Lesson)