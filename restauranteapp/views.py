from django.shortcuts import render
from .models import Plato
from django.shortcuts import render, redirect
from .models import Plato, Pedido
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth import logout


# Create your views here.

def go_home(request):
    return render(request, 'home.html')


def go_about_us(request):
    return render(request, 'about_us.html')


def go_carta(request):
    platos = Plato.objects.all()
    return render(request, 'carta.html', {'platos': platos})


def go_contacto(request):
    return render(request, 'contacto.html')


def go_registro(request):
    if request.method == 'POST':
        nombre = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'registro.html')

        try:
            usuario = Usuario.objects.create_user(email=email, nombre=nombre, rol='cliente', password=password)
            login(request, usuario)
            return redirect('home_page')
        except IntegrityError:
            messages.error(request, "Este correo electrónico ya está registrado.")
            return render(request, 'registro.html')

    return render(request, 'registro.html')


def go_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('home_page')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'login.html')

    return render(request, 'login.html')


def go_gestionar(request):
    return render(request, 'gestionar.html')


def guardar_pedido(request):
    if request.method == 'POST':
        pedido = Pedido.objects.create(total=0)

        total_pedido = 0

        for plato in Plato.objects.all():
            cantidad = int(request.POST.get(f'cantidad_{plato.id}', 0))
            if cantidad > 0:
                pedido.platos.add(plato)

                total_pedido += plato.precio * cantidad

        pedido.total = total_pedido
        pedido.save()

        return redirect('carta_page')


def cerrar_sesion(request):
    logout(request)
    return redirect('login_page')
