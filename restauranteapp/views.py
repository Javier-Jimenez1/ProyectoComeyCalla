from datetime import timezone, date  # Importa funciones para manejo de fechas y zonas horarias
from random import random  # Importa función para generar números aleatorios
from django import forms  # Importa el módulo de formularios de Django
from django.contrib import messages  # Importa el sistema de mensajes de Django
from django.contrib.auth import authenticate, login, logout  # Importa funciones para autenticación
from django.contrib.auth.decorators import login_required, \
    user_passes_test  # Importa decoradores para control de acceso
from django.contrib.auth.models import User, Group  # Importa modelos de usuario y grupos
from django.db import IntegrityError, transaction  # Importa manejo de errores y transacciones de BD
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden  # Importa clases para respuestas HTTP
from django.shortcuts import render, redirect, get_object_or_404  # Importa funciones para manejo de vistas
from django.views.decorators.http import require_POST  # Importa decorador para requerir método POST
from . import admin  # Importa el módulo admin de la aplicación actual
from .form import ReservaForm, ResenaForm
from .models import Usuario, Plato, Pedido, Mesa, PedidoPlato, Reserva, Resena, MenuDelDia  # Importa modelos locales
from django.utils import timezone  # Importa utilidades de zona horaria
from django.db.models import Sum  # Importa función para sumar valores
from django.utils.timezone import now  # Importa función para obtener fecha/hora actual
import random  # Importa módulo random para generación aleatoria



# Vista para la página de inicio
def go_home(request):
    return render(request, 'home.html')  # Renderiza la plantilla home.html


# Vista para la página "Sobre nosotros"
def go_about_us(request):
    return render(request, 'about_us.html')  # Renderiza la plantilla about_us.html


# Vista para mostrar la carta de platos
def go_carta(request):
    platos = Plato.objects.all()  # Obtiene todos los platos de la base de datos
    return render(request, 'carta.html', {'platos': platos})  # Renderiza carta.html con la lista de platos


# Vista para la página de contacto
def go_contacto(request):
    return render(request, 'contacto.html')  # Renderiza la plantilla contacto.html


# Vista para el registro de usuarios
def go_registro(request):
    if request.method == 'POST':  # Si la solicitud es POST (envío de formulario)
        nombre = request.POST['username']  # Obtiene nombre de usuario del formulario
        email = request.POST['email']  # Obtiene email del formulario
        password = request.POST['password']  # Obtiene contraseña del formulario
        confirm_password = request.POST['confirm_password']  # Obtiene confirmación de contraseña

        if password != confirm_password:  # Verifica que las contraseñas coincidan
            messages.error(request, "Las contraseñas no coinciden.")  # Muestra mensaje de error
            return render(request, 'registro.html')  # Vuelve a mostrar el formulario

        try:
            # Crea nuevo usuario con los datos proporcionados
            usuario = Usuario.objects.create_user(email=email, nombre=nombre, rol='cliente', password=password)
            login(request, usuario)  # Inicia sesión automáticamente al nuevo usuario
            return redirect('home_page')  # Redirige a la página de inicio
        except IntegrityError:  # Si el email ya existe
            messages.error(request, "Este correo electrónico ya está registrado.")
            return render(request, 'registro.html')

    return render(request, 'registro.html')  # Muestra el formulario de registro para GET


# Vista para el inicio de sesión
def go_login(request):
    if request.method == 'POST':  # Si la solicitud es POST (envío de formulario)
        email = request.POST['email']  # Obtiene email del formulario
        password = request.POST['password']  # Obtiene contraseña del formulario

        # Autentica al usuario con las credenciales proporcionadas
        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:  # Si la autenticación fue exitosa
            login(request, usuario)  # Inicia sesión
            if usuario.is_superuser:  # Si es superusuario (admin)
                return redirect('añadir_personal')  # Redirige al panel de administración
            else:
                return redirect('home_page')  # Redirige a la página de inicio para usuarios normales
        else:
            messages.error(request, "Correo o contraseña incorrectos.")  # Muestra mensaje de error
            return render(request, 'login.html')  # Vuelve a mostrar el formulario

    return render(request, 'login.html')  # Muestra el formulario de login para GET


# Vista para la página de gestión (probablemente para administradores)
def go_gestionar(request):
    return render(request, 'gestionar.html')  # Renderiza la plantilla gestionar.html


# Vista para guardar pedidos (requiere autenticación y método POST)
@login_required  # Solo usuarios autenticados pueden acceder
@require_POST  # Solo acepta solicitudes POST
def guardar_pedido(request):
    with transaction.atomic():  # Inicia transacción atómica para asegurar integridad de datos
        pedido = Pedido.objects.create(usuario=request.user)  # Crea un nuevo pedido asociado al usuario
        total_pedido = 0  # Inicializa el total del pedido

        # Procesa cada campo del formulario
        for key, value in request.POST.items():
            if key.startswith('cantidad_'):  # Busca campos de cantidad de platos
                try:
                    cantidad = int(value)  # Convierte la cantidad a entero
                    if cantidad > 0:  # Si la cantidad es válida
                        plato_id = key.split('_')[1]  # Obtiene el ID del plato
                        plato = Plato.objects.get(pk=plato_id)  # Obtiene el plato de la BD

                        # Crea o actualiza la relación entre pedido y plato
                        pedido_plato, created = PedidoPlato.objects.get_or_create(
                            pedido=pedido,
                            plato=plato,
                            defaults={'cantidad': cantidad}
                        )
                        if not created:  # Si ya existía la relación
                            pedido_plato.cantidad += cantidad  # Suma la nueva cantidad
                            pedido_plato.save()  # Guarda los cambios

                        total_pedido += plato.precio * cantidad  # Calcula el subtotal
                except (ValueError, Plato.DoesNotExist):  # Maneja errores
                    continue  # Continúa con el siguiente plato

        pedido.total = total_pedido  # Asigna el total calculado al pedido
        pedido.save()  # Guarda el pedido

    messages.success(request, "Pedido guardado correctamente.")  # Mensaje de éxito
    return redirect('pagina_pago', pedido_id=pedido.id)  # Redirige a la página de pago


# Función auxiliar para verificar si un usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.is_superuser  # True si es usuario autenticado y superusuario


# Vista para añadir personal (solo para superusuarios)
@login_required  # Requiere autenticación
@user_passes_test(lambda u: u.is_superuser)  # Solo para superusuarios
def añadir_personal(request):
    if request.method == 'POST':  # Si es una solicitud POST
        # Eliminación de usuario
        if 'eliminar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')  # Obtiene ID del usuario a eliminar
            try:
                usuario = Usuario.objects.get(id=usuario_id)  # Busca el usuario
                if usuario != request.user:  # Evita que el admin se elimine a sí mismo
                    usuario.delete()  # Elimina el usuario
                    messages.success(request, 'Usuario eliminado correctamente.')
                else:
                    messages.error(request, 'No puedes eliminarte a ti mismo.')
            except Usuario.DoesNotExist:  # Si el usuario no existe
                messages.error(request, 'Usuario no encontrado.')

        # Edición de usuario
        elif 'editar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')  # Obtiene ID del usuario a editar
            try:
                usuario = Usuario.objects.get(id=usuario_id)  # Busca el usuario
                usuario.nombre = request.POST.get('nombre')  # Actualiza nombre
                usuario.email = request.POST.get('email')  # Actualiza email
                usuario.rol = request.POST.get('rol').lower()  # Actualiza rol
                if request.POST.get('password'):  # Si se proporcionó nueva contraseña
                    usuario.set_password(request.POST.get('password'))  # Actualiza contraseña
                usuario.save()  # Guarda cambios
                messages.success(request, 'Usuario actualizado correctamente.')
            except Usuario.DoesNotExist:  # Si el usuario no existe
                messages.error(request, 'Usuario no encontrado.')

        # Creación de nuevo usuario
        else:
            nombre = request.POST.get('nombre')  # Obtiene nombre del formulario
            email = request.POST.get('email')  # Obtiene email
            rol = request.POST.get('rol').lower()  # Obtiene rol (en minúsculas)
            password = request.POST.get('password')  # Obtiene contraseña

            if Usuario.objects.filter(email=email).exists():  # Verifica si el email ya existe
                messages.warning(request, 'El correo ya está registrado.')
            else:
                # Crea nuevo usuario
                usuario = Usuario.objects.create_user(
                    nombre=nombre,
                    email=email,
                    rol=rol,
                    password=password
                )

                # Asigna grupo según el rol
                grupo, creado = Group.objects.get_or_create(name=rol)
                usuario.groups.add(grupo)

                messages.success(request, f'{rol.capitalize()} creado correctamente.')

    usuarios = Usuario.objects.all().order_by('rol', 'nombre')  # Obtiene todos los usuarios ordenados
    return render(request, 'añadir_personal.html', {'usuarios': usuarios})  # Renderiza plantilla con lista de usuarios


# Vista para añadir platos (requiere POST y permisos de staff)
@require_POST  # Solo acepta método POST
@login_required  # Requiere autenticación
def añadir_plato(request):
    if not request.user.is_staff:  # Verifica si el usuario tiene permisos de staff
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

    # Obtiene datos del formulario
    nombre = request.POST.get('nombre')
    precio = request.POST.get('precio')
    tipo = request.POST.get('tipo')
    descripcion = request.POST.get('descripcion', '')

    try:
        # Crea nuevo plato
        Plato.objects.create(
            nombre=nombre,
            precio=precio,
            tipo=tipo,
            descripcion=descripcion
        )
        messages.success(request, 'Plato añadido correctamente.')
    except Exception as e:  # Maneja errores
        messages.error(request, f'Error al añadir el plato: {str(e)}')

    return redirect('carta_page')  # Redirige a la página de la carta


# Vista para editar platos (requiere POST y permisos de staff)
@require_POST  # Solo acepta método POST
def editar_plato(request, plato_id):
    if not request.user.is_staff:  # Verifica permisos
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

    try:
        plato = Plato.objects.get(id=plato_id)  # Obtiene el plato a editar
        plato.nombre = request.POST.get('nombre')  # Actualiza nombre
        plato.precio = request.POST.get('precio')  # Actualiza precio
        plato.tipo = request.POST.get('tipo')  # Actualiza tipo
        plato.save()  # Guarda cambios
        return redirect('carta_page')  # Redirige a la carta
    except Plato.DoesNotExist:  # Si el plato no existe
        return redirect('carta_page')


# Vista para eliminar platos (requiere POST, autenticación y permisos de staff)
@require_POST  # Solo acepta método POST
@login_required  # Requiere autenticación
def eliminar_plato(request, plato_id):
    if not request.user.is_staff:  # Verifica permisos
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

    if not request.user.is_authenticated:  # Verifica autenticación
        return JsonResponse({'success': False, 'message': 'Autenticación requerida'}, status=401)

    try:
        plato = Plato.objects.get(id=plato_id)  # Obtiene el plato
        plato.delete()  # Elimina el plato
        return JsonResponse({'success': True, 'message': 'Plato eliminado correctamente'})
    except Plato.DoesNotExist:  # Si el plato no existe
        return JsonResponse({'success': False, 'message': 'Plato no encontrado'}, status=404)
    except Exception as e:  # Maneja otros errores
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Vista para login por rol (admin, camarero, cocinero)
def login_por_rol(request):
    rol = request.GET.get('rol')  # Obtiene el rol desde la URL

    if request.method == 'POST':  # Si es POST (envío de formulario)
        email = request.POST.get('email')  # Obtiene email
        password = request.POST.get('password')  # Obtiene contraseña

        usuario = authenticate(request, email=email, password=password)  # Autentica usuario

        if usuario is not None:  # Si la autenticación fue exitosa
            if rol == 'admin':  # Para administradores
                if usuario.is_superuser:  # Verifica si es superusuario
                    login(request, usuario)  # Inicia sesión
                    return redirect('añadir_personal')  # Redirige al panel de admin
                else:
                    messages.error(request, 'Solo los administradores pueden acceder aquí.')

            elif rol == 'camarero':  # Para camareros
                if usuario.is_superuser or Group.objects.filter(user=usuario, name='camarero').exists():
                    login(request, usuario)  # Inicia sesión
                    return redirect('camarero_panel')  # Redirige al panel de camarero
                else:
                    messages.error(request, 'No tienes permisos de camarero.')

            elif rol == 'cocinero':  # Para cocineros
                if usuario.is_superuser or Group.objects.filter(user=usuario, name='cocinero').exists():
                    login(request, usuario)  # Inicia sesión
                    return redirect('cocinero_panel')  # Redirige al panel de cocinero
                else:
                    messages.error(request, 'No tienes permisos de cocinero.')

            else:  # Rol no reconocido
                messages.error(request, 'Rol no reconocido.')

        else:  # Autenticación fallida
            messages.error(request, 'Credenciales inválidas.')

    return render(request, 'login_rol.html', {'rol': rol})  # Renderiza plantilla de login por rol


# Panel de cocinero (requiere autenticación)
@login_required
def cocinero_panel(request):
    # Obtiene todos los pedidos ordenados por fecha descendente
    pedidos = Pedido.objects.all().order_by('-fecha').prefetch_related('pedidoplato_set__plato')
    return render(request, 'cocinero_panel.html', {'pedidos': pedidos})  # Renderiza panel con lista de pedidos


# Cambiar estado de pedido (requiere POST y autenticación)
@require_POST
@login_required
def cambiar_estado_pedido(request):
    pedido_id = request.POST.get('pedido_id')  # Obtiene ID del pedido
    nuevo_estado = request.POST.get('nuevo_estado')  # Obtiene nuevo estado

    if nuevo_estado not in ['En preparación', 'Entregado']:  # Valida el estado
        return JsonResponse({'success': False, 'error': 'Estado no válido'})

    try:
        pedido = Pedido.objects.get(id=pedido_id)  # Obtiene el pedido
        pedido.estado = nuevo_estado  # Actualiza estado
        pedido.save()  # Guarda cambios
        return JsonResponse({'success': True, 'nuevo_estado': pedido.estado})
    except Pedido.DoesNotExist:  # Si el pedido no existe
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})


# Panel de camarero (requiere autenticación)
@login_required
def camarero_panel(request):
    # Obtiene todas las mesas ordenadas por número
    mesas = Mesa.objects.all().order_by('numero')
    return render(request, 'camarero_panel.html', {'mesas': mesas})  # Renderiza panel con lista de mesas


# Cambiar estado de mesa (requiere POST y autenticación)
@require_POST
@login_required
def cambiar_estado_mesa(request):
    mesa_id = request.POST.get('mesa_id')  # Obtiene ID de la mesa
    try:
        mesa = Mesa.objects.get(id=mesa_id)  # Obtiene la mesa

        if mesa.estado == 'Libre':  # Si está libre, la marca como ocupada
            mesa.estado = 'Ocupada'
            mesa.nombre_cliente = None
        else:  # Si está ocupada, la libera
            mesa.estado = 'Libre'
            mesa.nombre_cliente = None
        mesa.save()  # Guarda cambios
        return JsonResponse({'success': True, 'nuevo_estado': mesa.estado})
    except Mesa.DoesNotExist:  # Si la mesa no existe
        return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})


# Página de pago (requiere autenticación)
@login_required
def pagina_pago(request, pedido_id):
    # Obtiene el pedido o muestra error 404 si no existe o no pertenece al usuario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = PedidoPlato.objects.filter(pedido=pedido)  # Obtiene los platos del pedido
    contexto = {
        'pedido': pedido,
        'detalles': detalles,
    }
    return render(request, 'pago.html', contexto)  # Renderiza página de pago con los datos


# Historial de pedidos (requiere autenticación)
@login_required
def historial_pedidos(request):
    # Obtiene los pedidos del usuario ordenados por fecha descendente
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_pedidos.html', {'pedidos': pedidos})



# Lista de todas las reservas (requiere autenticación)
@login_required
def lista_reservas(request):
    # Obtiene todas las reservas ordenadas por fecha y hora
    reservas = Reserva.objects.all().order_by('fecha_reserva', 'hora_reserva')
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas})


# Mis reservas (requiere autenticación)
@login_required
def mis_reservas(request):
    # Obtiene las reservas del usuario actual ordenadas por fecha y hora
    reservas = Reserva.objects.filter(usuario=request.user).order_by('fecha_reserva', 'hora_reserva')
    return render(request, 'reservas/mis_reservas.html', {'reservas': reservas})


# Crear reserva (requiere autenticación)
@login_required
def crear_reserva(request):
    if request.method == 'POST':  # Si es POST (envío de formulario)
        form = ReservaForm(request.POST)  # Crea formulario con datos enviados
        if form.is_valid():  # Valida el formulario
            reserva = form.save(commit=False)  # Crea objeto reserva sin guardar
            reserva.usuario = request.user  # Asigna el usuario actual
            reserva.save()  # Guarda la reserva
            return redirect('mis_reservas')  # Redirige a "mis reservas"
    else:
        form = ReservaForm()  # Crea formulario vacío para GET
    return render(request, 'reservas/crear_editar_reserva.html', {'form': form})


# Editar reserva (requiere autenticación)
@login_required
def editar_reserva(request, reserva_id):
    # Obtiene la reserva o muestra error 404 si no existe o no pertenece al usuario
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)
    if request.method == 'POST':  # Si es POST (envío de formulario)
        form = ReservaForm(request.POST, instance=reserva)  # Crea formulario con datos y reserva existente
        if form.is_valid():  # Valida el formulario
            form.save()  # Guarda cambios
            return redirect('mis_reservas')  # Redirige a "mis reservas"
    else:
        form = ReservaForm(instance=reserva)  # Crea formulario con datos de la reserva
    return render(request, 'reservas/crear_editar_reserva.html', {'form': form})


# Eliminar reserva (requiere autenticación)
@login_required
def eliminar_reserva(request, reserva_id):
    # Obtiene la reserva o muestra error 404 si no existe o no pertenece al usuario
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)
    if request.method == 'POST':  # Si es POST (confirmación)
        reserva.delete()  # Elimina la reserva
        return redirect('mis_reservas')  # Redirige a "mis reservas"
    return render(request, 'reservas/confirmar_eliminacion.html', {'reserva': reserva})


# Recuperar contraseña
def recuperar_contraseña(request):
    if request.method == 'POST':  # Si es POST (envío de formulario)
        nombre = request.POST.get('nombre')  # Obtiene nombre de usuario
        nueva_contraseña = request.POST.get('nueva_contraseña')  # Obtiene nueva contraseña
        confirmar_contraseña = request.POST.get('confirmar_contraseña')  # Obtiene confirmación

        if nueva_contraseña != confirmar_contraseña:  # Verifica coincidencia
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            try:
                usuario = Usuario.objects.get(nombre=nombre)  # Busca usuario por nombre
                usuario.set_password(nueva_contraseña)  # Cambia contraseña
                usuario.save()  # Guarda cambios
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('login_page')  # Redirige a login
            except Usuario.DoesNotExist:  # Si el usuario no existe
                messages.error(request, 'No se encontró un usuario con ese nombre.')

    return render(request, 'recuperar_contraseña.html')  # Renderiza formulario de recuperación


# Listar reseñas (requiere autenticación)
@login_required
def listar_resenas(request):
    # Obtiene todas las reseñas ordenadas por fecha descendente
    resenas = Resena.objects.all().order_by('-fecha')
    return render(request, 'resenas/listar_resenas.html', {'resenas': resenas})


# Ver todas las reseñas
@login_required
def listar_resenas(request):
    resenas = Resena.objects.all().order_by('-fecha')
    return render(request, 'resenas/listar_resenas.html', {'resenas': resenas})


# Crear reseña
@login_required
def crear_resena(request):
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.usuario = request.user
            resena.fecha = timezone.now()
            resena.save()
            messages.success(request, "Reseña creada correctamente.")
            return redirect('listar_resenas')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ResenaForm()
    return render(request, 'resenas/crear_resena.html', {'form': form})


# Editar reseña
@login_required
def editar_resena(request, pk):
    resena = get_object_or_404(Resena, pk=pk)

    if resena.usuario != request.user:
        return HttpResponseForbidden("No puedes editar esta reseña.")

    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.fecha = timezone.now()
            resena.save()
            messages.success(request, "Reseña actualizada correctamente.")
            return redirect('mis_resenas')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ResenaForm(instance=resena)
    return render(request, 'resenas/editar_resena.html', {'form': form, 'resena': resena})


# Eliminar reseña
@login_required
def eliminar_resena(request, pk):
    resena = get_object_or_404(Resena, pk=pk)

    if resena.usuario != request.user:
        return HttpResponseForbidden("No puedes eliminar esta reseña.")

    if request.method == 'POST':
        resena.delete()
        messages.success(request, "Reseña eliminada correctamente.")
        return redirect('mis_resenas')
    return render(request, 'resenas/eliminar_resena.html', {'resena': resena})


# Listar reseñas del usuario
@login_required
def mis_resenas(request):
    resenas = Resena.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'resenas/mis_resenas.html', {'resenas': resenas})


# Repetir pedido (requiere autenticación)
@login_required
def repetir_pedido(request, pedido_id):
    # Obtiene el pedido original o muestra error 404
    pedido_original = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Crea nuevo pedido para el usuario actual
    nuevo_pedido = Pedido.objects.create(usuario=request.user, total=pedido_original.total)

    # Copia los platos del pedido original al nuevo
    platos_originales = PedidoPlato.objects.filter(pedido=pedido_original)
    for pp in platos_originales:
        PedidoPlato.objects.create(
            pedido=nuevo_pedido,
            plato=pp.plato,
            cantidad=pp.cantidad
        )

    return redirect('historial_pedidos')  # Redirige al historial


# Historial de pedidos con total gastado (requiere autenticación)
@login_required
def historial_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)  # Obtiene pedidos del usuario

    # Calcula el total gastado sumando todos los totales de pedidos
    total_gastado = pedidos.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'historial_pedidos.html', {
        'pedidos': pedidos,
        'total_gastado': total_gastado,
    })


# Platos más pedidos (requiere autenticación)
@login_required
def platos_favoritos(request):
    # Obtiene los 5 platos más pedidos sumando sus cantidades
    platos_mas_pedidos = (
        PedidoPlato.objects
        .values('plato__id', 'plato__nombre', 'plato__precio', 'plato__tipo')
        .annotate(total_pedidos=Sum('cantidad'))
        .order_by('-total_pedidos')[:5]
    )

    return render(request, 'platos_favoritos.html', {'platos': platos_mas_pedidos})


# Ver menú del día (requiere autenticación)
@login_required
def ver_menu_del_dia(request):
    # Obtiene el menú más reciente
    menu = MenuDelDia.objects.order_by('-fecha').first()
    return render(request, 'menu_del_dia.html', {'menu': menu})


# Generar menú del día aleatorio (requiere autenticación)
@login_required
def generar_menu_del_dia(request):
    hoy = date.today()  # Obtiene fecha actual
    # Verifica si ya existe menú para hoy
    if MenuDelDia.objects.filter(fecha=hoy).exists():
        menu = MenuDelDia.objects.get(fecha=hoy)  # Obtiene el menú existente
    else:
        todos_platos = list(Plato.objects.all())  # Obtiene todos los platos
        # Selecciona hasta 5 platos aleatorios
        seleccionados = random.sample(todos_platos, min(5, len(todos_platos)))

        # Crea nuevo menú con los platos seleccionados
        menu = MenuDelDia.objects.create(fecha=hoy)
        menu.platos.set(seleccionados)
        menu.save()

    return render(request, 'menu_del_dia.html', {'menu': menu})  # Muestra el menú