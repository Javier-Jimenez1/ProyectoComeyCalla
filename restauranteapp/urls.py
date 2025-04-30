
from django.contrib import admin
from django.urls import path

from restauranteapp.views import *

urlpatterns = [
    #URL , METODO , NOMBRE_CORTO
    path('home/', go_home , name='home_page'),
    path('aboutus/', go_about_us, name='about_us_page'),
    path('carta/', go_carta, name='carta_page'),
    path('contacto/', go_contacto, name='contacto_page'),
    path('login/', go_login, name='login_page'),
    path('registro/', go_registro, name='register_page'),
    path('gestionar/', go_gestionar, name='gestionar_page'),

]
