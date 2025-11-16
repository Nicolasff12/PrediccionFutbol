"""
Management command para poblar la base de datos con datos de prueba
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.partidos.models import Liga, Equipo, Partido


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba (Liga BetPlay, equipos y partidos)'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')
        
        # Crear Liga BetPlay
        liga, created = Liga.objects.get_or_create(
            nombre='Liga BetPlay Dimayor',
            pais='Colombia',
            defaults={'id_api': 1}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Liga creada: {liga.nombre}'))
        else:
            self.stdout.write(f'  Liga ya existe: {liga.nombre}')
        
        # Crear equipos
        equipos_data = [
            {'nombre': 'Millonarios FC', 'nombre_corto': 'MIL', 'id_api': 1},
            {'nombre': 'Atlético Nacional', 'nombre_corto': 'NAC', 'id_api': 2},
            {'nombre': 'América de Cali', 'nombre_corto': 'AME', 'id_api': 3},
            {'nombre': 'Deportivo Cali', 'nombre_corto': 'CAL', 'id_api': 4},
            {'nombre': 'Independiente Santa Fe', 'nombre_corto': 'SFE', 'id_api': 5},
            {'nombre': 'Junior de Barranquilla', 'nombre_corto': 'JUN', 'id_api': 6},
            {'nombre': 'Once Caldas', 'nombre_corto': 'ONC', 'id_api': 7},
            {'nombre': 'Tolima', 'nombre_corto': 'TOL', 'id_api': 8},
        ]
        
        equipos_creados = []
        for eq_data in equipos_data:
            equipo, created = Equipo.objects.get_or_create(
                id_api=eq_data['id_api'],
                defaults={
                    'nombre': eq_data['nombre'],
                    'nombre_corto': eq_data['nombre_corto']
                }
            )
            equipos_creados.append(equipo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Equipo creado: {equipo.nombre}'))
        
        # Crear partidos próximos
        ahora = timezone.now()
        partidos_data = [
            {
                'equipo_local': equipos_creados[0],  # Millonarios
                'equipo_visitante': equipos_creados[1],  # Nacional
                'fecha': ahora + timedelta(days=1, hours=20),
                'estado': 'NS'
            },
            {
                'equipo_local': equipos_creados[2],  # América
                'equipo_visitante': equipos_creados[3],  # Cali
                'fecha': ahora + timedelta(days=2, hours=18),
                'estado': 'NS'
            },
            {
                'equipo_local': equipos_creados[4],  # Santa Fe
                'equipo_visitante': equipos_creados[5],  # Junior
                'fecha': ahora + timedelta(days=3, hours=19),
                'estado': 'NS'
            },
            {
                'equipo_local': equipos_creados[6],  # Once Caldas
                'equipo_visitante': equipos_creados[7],  # Tolima
                'fecha': ahora + timedelta(days=4, hours=20),
                'estado': 'NS'
            },
        ]
        
        for partido_data in partidos_data:
            partido, created = Partido.objects.get_or_create(
                equipo_local=partido_data['equipo_local'],
                equipo_visitante=partido_data['equipo_visitante'],
                liga=liga,
                fecha=partido_data['fecha'],
                defaults={'estado': partido_data['estado']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[OK] Partido creado: {partido.equipo_local.nombre} vs {partido.equipo_visitante.nombre}'
                    )
                )
        
        # Crear algunos partidos finalizados
        partidos_finalizados = [
            {
                'equipo_local': equipos_creados[0],
                'equipo_visitante': equipos_creados[2],
                'fecha': ahora - timedelta(days=2),
                'goles_local': 2,
                'goles_visitante': 1,
                'estado': 'FT'
            },
            {
                'equipo_local': equipos_creados[1],
                'equipo_visitante': equipos_creados[3],
                'fecha': ahora - timedelta(days=1),
                'goles_local': 1,
                'goles_visitante': 1,
                'estado': 'FT'
            },
        ]
        
        for partido_data in partidos_finalizados:
            partido, created = Partido.objects.get_or_create(
                equipo_local=partido_data['equipo_local'],
                equipo_visitante=partido_data['equipo_visitante'],
                liga=liga,
                fecha=partido_data['fecha'],
                defaults={
                    'goles_local': partido_data['goles_local'],
                    'goles_visitante': partido_data['goles_visitante'],
                    'estado': partido_data['estado']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[OK] Partido finalizado creado: {partido.equipo_local.nombre} {partido.goles_local}-{partido.goles_visitante} {partido.equipo_visitante.nombre}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Datos de prueba creados exitosamente!'))
        self.stdout.write(f'\nResumen:')
        self.stdout.write(f'  - 1 Liga')
        self.stdout.write(f'  - {len(equipos_creados)} Equipos')
        self.stdout.write(f'  - {Partido.objects.count()} Partidos')

