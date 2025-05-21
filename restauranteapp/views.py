from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Usuario, Plato, Pedido, Mesa, PedidoPlato


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
                return redirect('añadir_personal')
            else:
                return redirect('home_page')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'login.html')

    return render(request, 'login.html')


def go_gestionar(request):
    return render(request, 'gestionar.html')


@login_required
@require_POST
def guardar_pedido(request):
    with transaction.atomic():
        pedido = Pedido.objects.create(usuario=request.user)
        total_pedido = 0

        for key, value in request.POST.items():
            if key.startswith('cantidad_'):
                try:
                    cantidad = int(value)
                    if cantidad > 0:
                        plato_id = key.split('_')[1]
                        plato = Plato.objects.get(pk=plato_id)
                        PedidoPlato.objects.create(pedido=pedido, plato=plato, cantidad=cantidad)
                        total_pedido += plato.precio * cantidad
                except (ValueError, Plato.DoesNotExist):
                    continue

        pedido.total = total_pedido
        pedido.save()

    messages.success(request, "Pedido guardado correctamente.")
    return redirect('pagina_pago', pedido_id=pedido.id)


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

            grupo, creado = Group.objects.get_or_create(name=rol)
            usuario.groups.add(grupo)

            messages.success(request, f'{rol.capitalize()} creado correctamente.')

    return render(request, 'añadir_personal.html')


@require_POST
def añadir_plato(request):
    nombre = request.POST.get('nombre')
    precio = request.POST.get('precio')
    tipo = request.POST.get('tipo')
    descripcion = request.POST.get('descripcion', '')

    try:
        Plato.objects.create(
            nombre=nombre,
            precio=precio,
            tipo=tipo,
            descripcion=descripcion
        )
        messages.success(request, 'Plato añadido correctamente.')
    except Exception as e:
        messages.error(request, f'Error al añadir el plato: {str(e)}')

    return redirect('carta_page')


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
@login_required
def eliminar_plato(request, plato_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Autenticación requerida'}, status=401)
    print(f"Intentando eliminar plato ID: {plato_id}")
    try:
        plato = Plato.objects.get(id=plato_id)
        plato.delete()
        print("Plato eliminado exitosamente")
        return JsonResponse({'success': True, 'message': 'Plato eliminado correctamente'})
    except Plato.DoesNotExist:
        print("Plato no encontrado")
        return JsonResponse({'success': False, 'message': 'Plato no encontrado'}, status=404)
    except Exception as e:
        print(f"Error al eliminar: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def login_por_rol(request):
    rol = request.GET.get('rol')

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


@login_required
def cocinero_panel(request):
    pedidos = Pedido.objects.all().order_by('-fecha').prefetch_related('pedidoplato_set__plato')
    return render(request, 'cocinero_panel.html', {'pedidos': pedidos})


@require_POST
@login_required
def cambiar_estado_pedido(request):
    pedido_id = request.POST.get('pedido_id')
    nuevo_estado = request.POST.get('nuevo_estado')

    if nuevo_estado not in ['En preparación', 'Entregado']:
        return JsonResponse({'success': False, 'error': 'Estado no válido'})

    try:
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
        return JsonResponse({'success': True, 'nuevo_estado': pedido.estado})
    except Pedido.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})


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

        if mesa.estado == 'Libre':
            mesa.estado = 'Ocupada'
            mesa.nombre_cliente = None
        else:
            mesa.estado = 'Libre'
            mesa.nombre_cliente = None
        mesa.save()
        return JsonResponse({'success': True, 'nuevo_estado': mesa.estado})
    except Mesa.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})


@login_required
def pagina_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = PedidoPlato.objects.filter(pedido=pedido)
    contexto = {
        'pedido': pedido,
        'detalles': detalles,
    }
    return render(request, 'pago.html', contexto)


@login_required
def historial_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_pedidos.html', {'pedidos': pedidos})
