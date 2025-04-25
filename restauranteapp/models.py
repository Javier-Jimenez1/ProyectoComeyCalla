# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
#
#
# # --- LOGIN Y REGISTRO ---- #
# class UsuarioManager(BaseUserManager):
#     def create_user(self, email, nombre, rol, password=None):
#         if not email:
#             raise ValueError("El usuario debe tener un email")
#         email = self.normalize_email(email)
#         usuario = self.model(email=email, nombre=nombre, rol=rol)
#         usuario.set_password(password)
#         usuario.save(using=self._db)
#         return usuario
#
#     def create_superuser(self, email, nombre, rol='admin', password=None):
#         usuario = self.create_user(email, nombre, rol, password)
#         usuario.is_superuser = True
#         usuario.is_staff = True
#         usuario.save(using=self._db)
#         return usuario
#
#
# class Usuario(AbstractBaseUser, PermissionsMixin):
#     ROLES = (
#         ('admin', 'Administrador'),
#         ('cliente', 'Cliente'),
#         ('camarero', 'Camarero'),
#     )
#     email = models.EmailField(max_length=255, unique=True)
#     nombre = models.CharField(max_length=255)
#     rol = models.CharField(max_length=255, choices=ROLES)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#
#     objects = UsuarioManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['nombre', 'rol']
#
#     def __str__(self):
#         return self.email + "-" + self.nombre + "-" + self.rol
#
#
# # --- BASE DE DATOS --- #
# class Categoria(models.Model):
#     nombre = models.CharField(max_length=50, unique=True)
#     icono = models.CharField(max_length=30, blank=True)  # Ej: 'fa-utensils' para FontAwesome
#
#     def __str__(self):
#         return self.nombre
#
#
# class Plato(models.Model):
#     nombre = models.CharField(max_length=100)
#     descripcion = models.TextField()
#     precio = models.DecimalField(max_digits=8, decimal_places=2)
#     categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
#     imagen = models.ImageField(upload_to='platos/')
#     disponible = models.BooleanField(default=True)
#     es_destacado = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"{self.nombre} - {self.precio}€"
#
# class Mesa(models.Model):
#     numero = models.PositiveIntegerField(unique=True)
#     capacidad = models.PositiveIntegerField()
#
#     def __str__(self):
#         return f"Mesa {self.numero} ({self.capacidad} personas)"
#
# class Reserva(models.Model):
#     ESTADOS = (
#         ('pendiente', 'Pendiente'),
#         ('confirmada', 'Confirmada'),
#         ('cancelada', 'Cancelada'),
#     )
#     cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True)
#     fecha = models.DateTimeField()
#     personas = models.PositiveIntegerField()
#     estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
#     comentarios = models.TextField(blank=True)
#     fecha_creacion = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Reserva #{self.id} - {self.cliente.nombre}"