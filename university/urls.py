from django.urls import path
from . import views


#university.urls

urlpatterns = [
    path('', views.home, name='home'), 
]