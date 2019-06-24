"""university_management_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from university import views

urlpatterns = [

    path('admin/login/', views.login_page, name='login_page'), #overwrite django path
    path('admin/login/?next=/admin/', views.login_page, name='login_page'), #overwrite django path

    path('admin/home', views.home_a, name='home_a'), 
    path('admin/consult', views.consult_a, name='consult_a'), 
    path('admin/university/', views.consult_uni_a, name='consult_uni_a'),  #overwrite django path
    path('admin/auth/', views.consult_auth_a, name='consult_auth_a'), #overwrite django path
    path('admin/insert', views.insert_a, name='insert_a'), 
    path('admin/operacoesBloco', views.operacoesBloco_a, name='operacoesBloco_a'), 
    path('admin/export', views.export_a, name='export'),
    path('admin/import_database', views.import_database_a, name='import_db_api'),
    path('admin/export_database', views.export_database_a, name='export_db_api'),


    path('admin/passwordchang', views.password_change, name='password_change_a'),

    path('admin/', admin.site.urls),
    path('', include('university.urls'))
]
