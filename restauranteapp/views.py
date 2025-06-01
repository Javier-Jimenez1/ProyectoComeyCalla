from datetime import timezone

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Usuario, Plato, Pedido, Mesa, PedidoPlato, Reserva, Resena
from django.utils import timezone
from django.db.models import Sum


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

                        pedido_plato, created = PedidoPlato.objects.get_or_create(
                            pedido=pedido,
                            plato=plato,
                            defaults={'cantidad': cantidad}
                        )
                        if not created:
                            pedido_plato.cantidad += cantidad
                            pedido_plato.save()

                        total_pedido += plato.precio * cantidad
                except (ValueError, Plato.DoesNotExist):
                    continue

        pedido.total = total_pedido
        pedido.save()

    messages.success(request, "Pedido guardado correctamente.")
    return redirect('pagina_pago', pedido_id=pedido.id)


def es_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(lambda u: u.is_superuser)
def añadir_personal(request):
    if request.method == 'POST':
        # Si es una solicitud para eliminar un usuario
        if 'eliminar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                if usuario != request.user:  # Prevenir que el admin se elimine a sí mismo
                    usuario.delete()
                    messages.success(request, 'Usuario eliminado correctamente.')
                else:
                    messages.error(request, 'No puedes eliminarte a ti mismo.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')

        # Si es una solicitud para editar un usuario
        elif 'editar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                usuario.nombre = request.POST.get('nombre')
                usuario.email = request.POST.get('email')
                usuario.rol = request.POST.get('rol').lower()
                if request.POST.get('password'):
                    usuario.set_password(request.POST.get('password'))
                usuario.save()
                messages.success(request, 'Usuario actualizado correctamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')

        # Si es una solicitud para añadir un nuevo usuario
        else:
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

    usuarios = Usuario.objects.all().order_by('rol', 'nombre')
    return render(request, 'añadir_personal.html', {'usuarios': usuarios})


@require_POST
@login_required
def añadir_plato(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

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
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

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
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

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


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_reserva', 'hora_reserva', 'numero_personas']
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={'type': 'date'}),
            'hora_reserva': forms.TimeInput(attrs={'type': 'time'}),
        }

@login_required
def lista_reservas(request):
    reservas = Reserva.objects.all().order_by('fecha_reserva', 'hora_reserva')
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas})

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('fecha_reserva', 'hora_reserva')
    return render(request, 'reservas/mis_reservas.html', {'reservas': reservas})

@login_required
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()
            return redirect('mis_reservas')
    else:
        form = ReservaForm()
    return render(request, 'reservas/crear_editar_reserva.html', {'form': form})

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return redirect('mis_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/crear_editar_reserva.html', {'form': form})

@login_required
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)
    if request.method == 'POST':
        reserva.delete()
        return redirect('mis_reservas')
    return render(request, 'reservas/confirmar_eliminacion.html', {'reserva': reserva})

def recuperar_contraseña(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')

        if nueva_contraseña != confirmar_contraseña:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            try:
                usuario = Usuario.objects.get(nombre=nombre)
                usuario.set_password(nueva_contraseña)
                usuario.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('login_page')
            except Usuario.DoesNotExist:
                messages.error(request, 'No se encontró un usuario con ese nombre.')

    return render(request, 'recuperar_contraseña.html')


@login_required
def listar_resenas(request):
    resenas = Resena.objects.all().order_by('-fecha')
    return render(request, 'resenas/listar_resenas.html', {'resenas': resenas})

@login_required
def crear_resena(request):
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario')
        if puntuacion and comentario:
            try:
                puntuacion = int(puntuacion)
                if 1 <= puntuacion <= 5:
                    Resena.objects.create(
                        usuario=request.user,
                        puntuacion=puntuacion,
                        comentario=comentario,
                        fecha=timezone.now()
                    )
                    return redirect('listar_resenas')
            except ValueError:
                pass  # Puedes agregar validación adicional o mensajes
    return render(request, 'resenas/crear_resena.html')

@login_required
def editar_resena(request, pk):
    resena = get_object_or_404(Resena, pk=pk)

    if resena.usuario != request.user:
        return HttpResponseForbidden("No puedes editar esta reseña.")

    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario')
        if puntuacion and comentario:
            try:
                puntuacion = int(puntuacion)
                if 1 <= puntuacion <= 5:
                    resena.puntuacion = puntuacion
                    resena.comentario = comentario
                    resena.fecha = timezone.now()
                    resena.save()
                    return redirect('mis_resenas')
            except ValueError:
                pass
    return render(request, 'resenas/editar_resena.html', {'resena': resena})

@login_required
def eliminar_resena(request, pk):
    resena = get_object_or_404(Resena, pk=pk)
    if resena.usuario != request.user:
        return HttpResponseForbidden("No puedes eliminar esta reseña.")

    if request.method == 'POST':
        resena.delete()
        return redirect('mis_resenas')
    return render(request, 'resenas/eliminar_resena.html', {'resena': resena})

@login_required
def mis_resenas(request):
    resenas = Resena.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'resenas/../templates/mis_resenas.html', {'resenas': resenas})

@login_required
def mis_resenas(request):
    resenas = Resena.objects.filter(usuario=request.user).order_by('-fecha')  # Ordena por fecha descendente
    return render(request, 'mis_resenas.html', {'resenas': resenas})


@login_required
def repetir_pedido(request, pedido_id):
    pedido_original = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Crear nuevo pedido para el usuario actual
    nuevo_pedido = Pedido.objects.create(usuario=request.user, total=pedido_original.total)

    # Copiar los platos del pedido original
    platos_originales = PedidoPlato.objects.filter(pedido=pedido_original)
    for pp in platos_originales:
        PedidoPlato.objects.create(pedido=nuevo_pedido, plato=pp.plato, cantidad=pp.cantidad)

    return redirect('historial_pedidos')  # o donde quieras redirigir tras repetir

@login_required
def historial_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_pedidos.html', {'pedidos': pedidos})

@login_required
def platos_favoritos(request):
    platos_mas_pedidos = (
        PedidoPlato.objects
        .values('plato__id', 'plato__nombre', 'plato__precio', 'plato__tipo')
        .annotate(total_pedidos=Sum('cantidad'))
        .order_by('-total_pedidos')[:5]  # Top 5 más pedidos
    )

    return render(request, 'platos_favoritos.html', {'platos': platos_mas_pedidos})
