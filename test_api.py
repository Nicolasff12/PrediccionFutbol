"""
Script de prueba para verificar la conexión con la API de BeSoccer
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prediccion_futbol.settings')
django.setup()

from apps.partidos.services import BesoccerService
import json

def test_api():
    """Prueba la conexión con la API de BeSoccer"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN CON API BESOCCER")
    print("=" * 60)
    
    service = BesoccerService()
    
    # Verificar que la API key está configurada
    if not service.api_key:
        print("[ERROR] BESOCCER_API_KEY no esta configurada")
        return False
    
    print(f"[OK] API Key configurada: {service.api_key[:10]}...")
    print()
    
    # Prueba 1: Obtener ligas de Colombia
    print("1. Probando obtener ligas de Colombia...")
    try:
        ligas = service.obtener_ligas("Colombia")
        if ligas:
            print(f"   [OK] Se encontraron {len(ligas)} ligas")
            for liga in ligas[:3]:  # Mostrar solo las primeras 3
                print(f"      - {liga.get('name', 'N/A')} (ID: {liga.get('id', 'N/A')})")
        else:
            print("   [WARN] No se encontraron ligas")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    print()
    
    # Prueba 2: Obtener Liga BetPlay
    print("2. Probando obtener Liga BetPlay...")
    try:
        liga_betplay = service.obtener_liga_betplay()
        if liga_betplay:
            print(f"   [OK] Liga BetPlay encontrada:")
            print(f"      - Nombre: {liga_betplay.get('name', 'N/A')}")
            print(f"      - ID: {liga_betplay.get('id', 'N/A')}")
            liga_id = liga_betplay.get('id')
        else:
            print("   [WARN] Liga BetPlay no encontrada")
            liga_id = None
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    print()
    
    if not liga_id:
        print("[WARN] No se puede continuar sin el ID de la liga")
        return False
    
    # Prueba 3: Obtener equipos de la liga
    print("3. Probando obtener equipos de la liga...")
    try:
        equipos = service.obtener_equipos_liga(liga_id)
        if equipos:
            print(f"   [OK] Se encontraron {len(equipos)} equipos")
            for equipo in equipos[:5]:  # Mostrar solo los primeros 5
                print(f"      - {equipo.get('name', 'N/A')} (ID: {equipo.get('id', 'N/A')})")
        else:
            print("   [WARN] No se encontraron equipos")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        print(f"   Detalle: {str(e)}")
        return False
    
    print()
    
    # Prueba 4: Obtener próximos partidos
    print("4. Probando obtener proximos partidos...")
    try:
        partidos = service.obtener_partidos_proximos(liga_id, dias=7)
        if partidos:
            print(f"   [OK] Se encontraron {len(partidos)} partidos proximos")
            for partido in partidos[:3]:  # Mostrar solo los primeros 3
                local = partido.get('home_team', {}).get('name', 'N/A')
                visitante = partido.get('away_team', {}).get('name', 'N/A')
                fecha = partido.get('date', 'N/A')
                print(f"      - {local} vs {visitante} ({fecha})")
        else:
            print("   [WARN] No se encontraron partidos proximos")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        print(f"   Detalle: {str(e)}")
        return False
    
    print()
    
    # Prueba 5: Obtener partidos coming
    print("5. Probando obtener partidos coming...")
    try:
        partidos_coming = service.obtener_partidos_coming(liga_id, limite=5)
        if partidos_coming:
            print(f"   [OK] Se encontraron {len(partidos_coming)} partidos coming")
        else:
            print("   [WARN] No se encontraron partidos coming (puede ser normal si el endpoint no existe)")
    except Exception as e:
        print(f"   [WARN] Error (puede ser normal si el endpoint no existe): {e}")
    
    print()
    
    # Prueba 6: Obtener tabla de posiciones
    print("6. Probando obtener tabla de posiciones...")
    try:
        tabla = service.obtener_tabla_posiciones(liga_id)
        if tabla:
            print(f"   [OK] Se encontraron {len(tabla)} equipos en la tabla")
            for item in tabla[:3]:  # Mostrar solo los primeros 3
                equipo = item.get('team_name', 'N/A')
                posicion = item.get('position', 'N/A')
                puntos = item.get('points', 'N/A')
                print(f"      - {posicion}. {equipo} ({puntos} pts)")
        else:
            print("   [WARN] No se encontro tabla de posiciones")
    except Exception as e:
        print(f"   [WARN] Error (puede ser normal si el endpoint no existe): {e}")
    
    print()
    print("=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)
    return True

if __name__ == '__main__':
    test_api()

