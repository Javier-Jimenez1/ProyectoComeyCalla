from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from restauranteapp import views

urlpatterns = [
    # Páginas principales
    path('home/', views.go_home, name='home_page'),
    path('aboutus/', views.go_about_us, name='about_us_page'),
    path('carta/', views.go_carta, name='carta_page'),
    path('contacto/', views.go_contacto, name='contacto_page'),
    path('gestionar/', views.go_gestionar, name='gestionar_page'),

    # Autenticación personalizada
    path('login/', views.go_login, name='login_page'),
    path('logout/', LogoutView.as_view(next_page='home_page'), name='logout'),
    path('registro/', views.go_registro, name='register_page'),

    # Funcionalidades adicionales
    path('guardar_pedido/', views.guardar_pedido, name='guardar_pedido'),
    path('añadir_personal/', views.añadir_personal, name='añadir_personal'),
    path('admin/', admin.site.urls),
    path('login-rol/', views.login_por_rol, name='login_rol'),
    path('cocinero/panel/', views.cocinero_panel, name='cocinero_panel'),
    path('camarero/', views.camarero_panel, name='camarero_panel'),
    path('editar-plato/<int:plato_id>/', views.editar_plato, name='editar_plato'),
    path('eliminar-plato/<int:plato_id>/', views.eliminar_plato, name='eliminar_plato'),
    path('añadir-plato/', views.añadir_plato, name='añadir_plato'),
    path('cambiar-estado-mesa/', views.cambiar_estado_mesa, name='cambiar_estado_mesa'),
    path('pago/<int:pedido_id>/', views.pagina_pago, name='pagina_pago'),
    path('cambiar-estado-pedido/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('historial-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('reservas/', views.lista_reservas, name='lista_reservas'),  # Todas las reservas
    path('mis_reservas/', views.mis_reservas, name='mis_reservas'),  # Mis reservas
    path('reservas/crear/', views.crear_reserva, name='crear_reserva'),
    path('reservas/editar/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('reservas/eliminar/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('recuperar-contraseña/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('resenas/', views.listar_resenas, name='listar_resenas'),
    path('resenas/crear/', views.crear_resena, name='crear_resena'),
    path('resenas/mis/', views.mis_resenas, name='mis_resenas'),
    path('resenas/editar/<int:pk>/', views.editar_resena, name='editar_resena'),
    path('resenas/eliminar/<int:pk>/', views.eliminar_resena, name='eliminar_resena'),
    path('repetir_pedido/<int:pedido_id>/', views.repetir_pedido, name='repetir_pedido'),
    path('platos-favoritos/', views.platos_favoritos, name='platos_favoritos'),
    path('menu-del-dia/', views.generar_menu_del_dia, name='menu_del_dia')

]
