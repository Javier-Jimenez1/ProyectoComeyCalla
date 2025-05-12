from django.shortcuts import render
from .models import Plato
from django.shortcuts import render, redirect
from .models import Plato, Pedido


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
    return render(request, 'registro.html')

def go_login(request):
    return render(request, 'login.html')

def go_gestionar(request):
    return render(request, 'gestionar.html')


def guardar_pedido(request):
    if request.method == 'POST':
        # Crear un nuevo pedido
        pedido = Pedido.objects.create(total=0)

        # Inicializar el total del pedido
        total_pedido = 0

        # Iterar sobre los platos y las cantidades seleccionadas
        for plato in Plato.objects.all():
            cantidad = int(request.POST.get(f'cantidad_{plato.id}', 0))
            if cantidad > 0:
                # Añadir el plato al pedido
                pedido.platos.add(plato)

                # Calcular el total del pedido
                total_pedido += plato.precio * cantidad

        # Asignar el total al pedido
        pedido.total = total_pedido
        pedido.save()  # Guardar el pedido

        # Redirigir a la carta u otra página después de guardar el pedido
        return redirect('carta_page')
