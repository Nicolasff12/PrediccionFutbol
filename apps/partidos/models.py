from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Equipo(models.Model):
    """Modelo para equipos de fútbol"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    nombre_corto = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nombre corto')
    escudo = models.URLField(blank=True, null=True, verbose_name='URL del escudo')
    id_api = models.IntegerField(unique=True, verbose_name='ID en API')
    
    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Liga(models.Model):
    """Modelo para ligas de fútbol"""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    pais = models.CharField(max_length=50, verbose_name='País')
    logo = models.URLField(blank=True, null=True, verbose_name='URL del logo')
    id_api = models.IntegerField(unique=True, verbose_name='ID en API')
    
    class Meta:
        verbose_name = 'Liga'
        verbose_name_plural = 'Ligas'
        ordering = ['pais', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.pais})"


class Partido(models.Model):
    """Modelo para partidos de fútbol"""
    ESTADO_CHOICES = [
        ('NS', 'No iniciado'),
        ('LIVE', 'En vivo'),
        ('FT', 'Finalizado'),
        ('POST', 'Postpuesto'),
        ('CANC', 'Cancelado'),
    ]
    
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_local', verbose_name='Equipo local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitante', verbose_name='Equipo visitante')
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name='partidos', verbose_name='Liga')
    fecha = models.DateTimeField(verbose_name='Fecha y hora')
    goles_local = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Goles local')
    goles_visitante = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Goles visitante')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='NS', verbose_name='Estado')
    id_api = models.IntegerField(unique=True, blank=True, null=True, verbose_name='ID en API')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha', 'estado']),
            models.Index(fields=['liga', '-fecha']),
        ]
    
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def resultado(self):
        """Retorna el resultado del partido"""
        if self.estado == 'FT':
            return f"{self.goles_local} - {self.goles_visitante}"
        return "Por jugar"

