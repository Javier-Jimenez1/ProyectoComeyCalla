from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User

from ProyectoComeyCalla import settings


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, rol, password=None):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        usuario = self.model(email=email, nombre=nombre, rol=rol)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, rol='admin', password=None):
        usuario = self.create_user(email, nombre, rol, password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Administrador'),
        ('cocinero', 'Cocinero'),
        ('camarero', 'Camarero'),
        ('cliente', 'Cliente'),
    )
    email = models.EmailField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    rol = models.CharField(max_length=10, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'rol']

    def __str__(self):
        return self.email


class Plato(models.Model):
    TIPO_PLATO = (
        ('tapa', 'Tapa'),
        ('principal', 'Plato principal'),
        ('postre', 'Postre'),
        ('bebida', 'Bebida'),
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_PLATO)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - {self.precio}€"


class Mesa(models.Model):
    ESTADOS = (
        ('Libre', 'Libre'),
        ('Ocupada', 'Ocupada'),
    )

    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Libre')

    def __str__(self):
        return f"Mesa {self.numero} - {self.estado}"


class Pedido(models.Model):
    ESTADOS = (
        ('En preparación', 'En preparación'),
        ('Entregado', 'Entregado'),
    )

    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='En preparación')
    platos = models.ManyToManyField('Plato', through='PedidoPlato')


class PedidoPlato(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        unique_together = ('pedido', 'plato')


class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_personas = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reserva de {self.usuario.username} para {self.numero_personas} personas el {self.fecha_reserva} a las {self.hora_reserva}'



