from django.shortcuts import render

# Create your views here.

def go_home(request):
    return render(request, 'home.html')

def go_navbar(request):
    return render(request, 'navbar.html')

def go_about_us(request):
    return render(request, 'about_us.html')

def go_carta(request):
    return render(request, 'carta.html')

def go_contacto(request):
    return render(request, 'contacto.html')

def go_registro(request):
    return render(request, 'registro.html')

def go_login(request):
    return render(request, 'login.html')