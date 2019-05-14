from django.urls import path
from . import views


#university.urls

urlpatterns = [
    path('', views.login_page, name='login'), 
    path('logout', views.logout_user, name='logout'),

    path('profile', views.profile, name='profile'), 

    path('student/consult_details', views.consult_details_s, name='consult_details_s'), 
    path('student/consult_contacts', views.consult_details_s, name='consult_contacts'), 
    path('student/consult_courses', views.consult_details_s, name='consult_courses'), 
    path('student/consult_university', views.consult_details_s, name='consult_university'),
    path('student/home', views.home_s, name='home_s'), 
    path('student/password_alt', views.password_alt_s, name='password_alt_s'), 

    path('teacher/consult_details', views.consult_details_t, name='consult_details_t'), 
    path('teacher/consult_contacts', views.consult_details_t, name='consult_contacts'), 
    path('teacher/home', views.home_t, name='home_t'), 
    path('teacher/password_alt', views.password_alt_t, name='password_alt_t')
]

