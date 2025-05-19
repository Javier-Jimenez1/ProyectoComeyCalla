from django.contrib import admin
from django.urls import path
from restauranteapp import views
from django.contrib.auth.views import LogoutView
from django.urls import path, include

urlpatterns = [
    # Páginas principales
    path('home/', views.go_home, name='home_page'),
    path('aboutus/', views.go_about_us, name='about_us_page'),
    path('carta/', views.go_carta, name='carta_page'),
    path('contacto/', views.go_contacto, name='contacto_page'),
    path('gestionar/', views.go_gestionar, name='gestionar_page'),

    # Autenticación personalizada
    path('login/', views.go_login, name='login_page'),
    path('logout/', LogoutView.as_view(next_page='login_page'), name='logout'),
    path('registro/', views.go_registro, name='register_page'),

    # Funcionalidades adicionales
    path('guardar_pedido/', views.guardar_pedido, name='guardar_pedido'),
    path('admin-personal/', views.añadir_personal, name='añadir_personal'),
    path('admin/', admin.site.urls),
    path('login-rol/', views.login_por_rol, name='login_rol'),
    path('cocinero/panel/', views.cocinero_panel, name='cocinero_panel'),
    path('camarero/', views.camarero_panel, name='camarero_panel'),
    path('editar-plato/<int:plato_id>/', views.editar_plato, name='editar_plato'),
    path('eliminar-plato/<int:plato_id>/', views.eliminar_plato, name='eliminar_plato'),
    path('cambiar-estado-mesa/', views.cambiar_estado_mesa, name='cambiar_estado_mesa'),
    path('pago/<int:pedido_id>/', views.pagina_pago, name='pagina_pago'),
    path('cambiar-estado-pedido/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

]
