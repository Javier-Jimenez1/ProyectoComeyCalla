
from django.contrib import admin
from django.urls import path

from restauranteapp.views import *

urlpatterns = [
    #URL , METODO , NOMBRE_CORTO
    path('home/', go_home , name='home_page'),
    path('navbar/', go_navbar, name='navbar_page'),
]
