from django.urls import path
from . import views


#university.urls

urlpatterns = [
    path('', views.login_page, name='login'), 
    path('logout', views.logout_user, name='logout'),

    path('student/home', views.home_s, name='home_s'), 
    path('student/inscricoes_subject', views.inscricoes_subject_s, name='inscricoes_subject_s'),
    path('student/choose_lessons', views.choose_lessons_s, name='choose_lessons_s'),
    path('student/inscricoes_confirmacao', views.inscricoes_confirmacao_s, name='inscricoes_confirmacao_s'), #so para verificar dados
    path('student/horario', views.horario_atual, name='horario_atual_s'),
    path('student/consult_presencas', views.consult_presencas_s, name='consult_presencas_s'),
    path('student/consult_contacts', views.consult_contacts_s, name='consult_contacts_s'),
    path('student/consult_details', views.consult_details_s, name='consult_details_s'), 
    path('student/consult_subjects', views.consult_subjects_s, name='consult_subjects_s'),
    path('student/consult_university', views.consult_university_s, name='consult_university_s'),
    path('student/request_change_lesson', views.request_change_lesson_s, name='request_change_lesson_s'),
    path('student/estadoPedidos', views.estado_pedidos_s, name='estado_pedidos_s'),
    path('student/passwordchang', views.password_change, name='password_change_s'),
    path('student/apagar', views.apagar_s, name='apagar_s'),
    

    path('teacher/home', views.home_t, name='home_t'), 
    path('teacher/horario', views.horario_atual, name='horario_atual_t'),
    path('teacher/consult_contacts', views.consult_contacts_t, name='consult_contacts_t'),
    path('teacher/consult_details', views.consult_details_t, name='consult_details_t'),
    path('teacher/consult_turmas', views.consult_turmas_t, name='consult_turmas_t'),
    path('teacher/fechar_turma', views.fechar_turma_t, name='fechar_turma_t'),
    path('teacher/resposta_pedidos', views.resposta_pedidos_t, name='resposta_pedidos_t'),
    path('teacher/enviar_pedidos', views.enviar_pedidos_t, name='enviar_pedidos_t'),
    path('teacher/presencas_consultar', views.presencas_consultar_t, name='presencas_consultar_t'),
    path('teacher/presencas_registar', views.presencas_registar_t, name='presencas_registar_t'),
    path('teacher/passwordchang', views.password_change, name='password_change_t'),
]

#/(?P<bus_number>\w+)
#/(?P<value>\d+)/ int
#\s+ str
#^(?P<num>\d+)|/$
