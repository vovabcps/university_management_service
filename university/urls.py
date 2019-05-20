from django.urls import path
from . import views


#university.urls

urlpatterns = [
    path('', views.login_page, name='login'), 
    path('logout', views.logout_user, name='logout'),

    path('student/home', views.home_s, name='home_s'), 
    path('student/inscricoes_subject', views.inscricoes_subject_s, name='inscricoes_subject_s'),
    path('student/consult_contacts', views.consult_contacts_s, name='consult_contacts_s'),
    path('student/consult_details', views.consult_details_s, name='consult_details_s'), 
    path('student/consult_subjects', views.consult_subjects_s, name='consult_subjects_s'),
    path('student/consult_university', views.consult_university_s, name='consult_university_s'),
    path('student/passwordchang', views.password_change, name='password_change_s'),
    

    path('teacher/home', views.home_t, name='home_t'), 
    path('teacher/consult_contacts', views.consult_contacts_t, name='consult_contacts_t'),
    path('teacher/consult_details', views.consult_details_t, name='consult_details_t'), 
    path('teacher/passwordchang', views.password_change, name='password_change_t'),
]

