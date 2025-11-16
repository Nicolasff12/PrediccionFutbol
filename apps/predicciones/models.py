from django.db import models
from django.contrib.auth import get_user_model
from apps.partidos.models import Partido

Usuario = get_user_model()


class Prediccion(models.Model):
    """Modelo para predicciones de partidos realizadas por usuarios"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='predicciones', verbose_name='Usuario')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='predicciones', verbose_name='Partido')
    goles_local_predicho = models.IntegerField(verbose_name='Goles local predicho')
    goles_visitante_predicho = models.IntegerField(verbose_name='Goles visitante predicho')
    prediccion_ia = models.TextField(blank=True, null=True, verbose_name='Análisis de IA')
    confianza = models.FloatField(
        default=0.0,
        verbose_name='Nivel de confianza',
        help_text='Nivel de confianza de la predicción (0-100)'
    )
    fecha_prediccion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de predicción')
    es_correcta = models.BooleanField(null=True, blank=True, verbose_name='¿Predicción correcta?')
    
    class Meta:
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'
        ordering = ['-fecha_prediccion']
        unique_together = ['usuario', 'partido']
        indexes = [
            models.Index(fields=['usuario', '-fecha_prediccion']),
            models.Index(fields=['partido']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.partido} - {self.goles_local_predicho}:{self.goles_visitante_predicho}"
    
    def verificar_prediccion(self):
        """Verifica si la predicción fue correcta"""
        if self.partido.estado == 'FT':
            correcta = (
                self.goles_local_predicho == self.partido.goles_local and
                self.goles_visitante_predicho == self.partido.goles_visitante
            )
            self.es_correcta = correcta
            self.save()
            return correcta
        return None

