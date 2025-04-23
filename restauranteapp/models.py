from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


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