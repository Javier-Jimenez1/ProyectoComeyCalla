from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from .models import Plato, PedidoPlato
from django.shortcuts import render, redirect
from .models import Plato, Pedido
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth import logout
from restauranteapp.models import Usuario
from django.http import HttpResponse
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Mesa


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
            if usuario.is_superuser:
                return redirect('añadir_personal')  # Redirige al panel admin si es superuser
            else:
                return redirect('home_page')  # Resto de usuarios van al home
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'login.html')

    return render(request, 'login.html')


def go_gestionar(request):
    return render(request, 'gestionar.html')


@login_required
def guardar_pedido(request):
    if request.method == 'POST':
        # Crear el pedido asociado al usuario actual
        pedido = Pedido.objects.create(
            cliente=request.user,
            total=0
        )

        total_pedido = 0
        items_pedido = []

        for plato in Plato.objects.all():
            cantidad = int(request.POST.get(f'cantidad_{plato.id}', 0))
            if cantidad > 0:
                # Añadir el plato al pedido con la cantidad
                PedidoPlato.objects.create(
                    pedido=pedido,
                    plato=plato,
                    cantidad=cantidad
                )
                total_pedido += plato.precio * cantidad

        # Actualizar el total del pedido
        pedido.total = total_pedido
        pedido.save()

        messages.success(request, 'Pedido guardado correctamente.')
        return redirect('detalle_pedido', pedido_id=pedido.id)

    return redirect('carta_page')


def cerrar_sesion(request):
    logout(request)
    return redirect('login_page')


def es_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(lambda u: u.is_superuser)
def añadir_personal(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        rol = request.POST.get('rol').lower()
        password = request.POST.get('password')

        if Usuario.objects.filter(email=email).exists():
            messages.warning(request, 'El correo ya está registrado.')
        else:
            usuario = Usuario.objects.create_user(
                nombre=nombre,
                email=email,
                rol=rol,
                password=password
            )

            # Asignar al grupo correspondiente
            grupo, creado = Group.objects.get_or_create(name=rol)
            usuario.groups.add(grupo)

            messages.success(request, f'{rol.capitalize()} creado correctamente.')

    return render(request, 'añadir_personal.html')


@require_POST
def editar_plato(request, plato_id):
    try:
        plato = Plato.objects.get(id=plato_id)
        plato.nombre = request.POST.get('nombre')
        plato.precio = request.POST.get('precio')
        plato.tipo = request.POST.get('tipo')
        plato.save()
        return redirect('carta_page')
    except Plato.DoesNotExist:
        return redirect('carta_page')


@require_POST
def eliminar_plato(request, plato_id):
    try:
        plato = Plato.objects.get(id=plato_id)
        plato.delete()
        return JsonResponse({'status': 'success'})
    except Plato.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Plato no encontrado'}, status=404)


def login_por_rol(request):
    rol = request.GET.get('rol')  # 'camarero', 'cocinero', 'admin'

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:
            if rol == 'admin':
                if usuario.is_superuser:
                    login(request, usuario)
                    return redirect('añadir_personal')
                else:
                    messages.error(request, 'Solo los administradores pueden acceder aquí.')

            elif rol == 'camarero':
                if usuario.is_superuser or Group.objects.filter(user=usuario, name='camarero').exists():
                    login(request, usuario)
                    return redirect('camarero_panel')
                else:
                    messages.error(request, 'No tienes permisos de camarero.')

            elif rol == 'cocinero':
                if usuario.is_superuser or Group.objects.filter(user=usuario, name='cocinero').exists():
                    login(request, usuario)
                    return redirect('cocinero_panel')
                else:
                    messages.error(request, 'No tienes permisos de cocinero.')

            else:
                messages.error(request, 'Rol no reconocido.')

        else:
            messages.error(request, 'Credenciales inválidas.')

    return render(request, 'login_rol.html', {'rol': rol})


def cocinero_panel(request):
    return render(request, 'cocinero_panel.html')


@login_required
def camarero_panel(request):
    mesas = Mesa.objects.all().order_by('numero')
    return render(request, 'camarero_panel.html', {'mesas': mesas})


@require_POST
@login_required
def cambiar_estado_mesa(request):
    mesa_id = request.POST.get('mesa_id')
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        # Cambiar estado: si está Libre -> Ocupada, si está Ocupada -> Libre
        if mesa.estado == 'Libre':
            mesa.estado = 'Ocupada'
            mesa.nombre_cliente = None  # Si quieres limpiar el cliente al cambiar estado
        else:
            mesa.estado = 'Libre'
            mesa.nombre_cliente = None
        mesa.save()
        return JsonResponse({'success': True, 'nuevo_estado': mesa.estado})
    except Mesa.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})


@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Verificar que el usuario tiene permiso para ver este pedido
    if not (request.user.is_staff or pedido.cliente == request.user):
        raise PermissionDenied

    return render(request, 'detalle_pedido.html', {'pedido': pedido})


@login_required
def listar_pedidos(request):
    if request.user.is_staff:
        # Staff puede ver todos los pedidos
        pedidos = Pedido.objects.all().order_by('-fecha')
    else:
        # Usuarios normales solo ven sus pedidos
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha')

    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS).keys():
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, 'Estado del pedido actualizado.')

    return redirect('detalle_pedido', pedido_id=pedido.id)
