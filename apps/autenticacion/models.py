from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato de teléfono inválido")],
        verbose_name='Teléfono'
    )
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name='Foto de perfil')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    es_activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.username

