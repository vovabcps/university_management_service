from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),

    path('logout', views.logout_user, name='logout'),

    path('profile', views.profile, name='profile'), 

    path('student/consult_details', views.consult_details_s, name='consult_details_s'), 
    path('student/home', views.home_s, name='home_s'), 
    path('student/password_alt', views.password_alt_s, name='password_alt_s'), 

    path('teacher/consult_details', views.consult_details_t, name='consult_details_t'), 
    path('teacher/home', views.home_t, name='home_t'), 
    path('teacher/password_alt', views.password_alt_t, name='password_alt_t'), 

    path('admin/home', views.home_a, name='home_a'), 
    path('admin/consult_details', views.consult_details_a, name='consult_details_a'), 
    path('admin/consult_students', views.consult_students_a, name='consult_students_a'), 
    path('admin/consult_teachers', views.consult_teachers_a, name='consult_teachers_a'), 
    path('admin/insert_students', views.insert_students_a, name='insert_students_a'), 
    path('admin/insert_teachers', views.insert_teachers_a, name='insert_teachers_a'), 
    path('admin/password_alt', views.password_alt_a, name='password_alt_a'), 

]
