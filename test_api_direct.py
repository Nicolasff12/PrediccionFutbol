"""
Script para probar directamente la API de BeSoccer y ver qué endpoints funcionan
"""
import requests
import json

API_KEY = "fbe606a6eda33a3a249cfdb242d4f163"
BASE_URL = "https://api.besoccer.com"

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def test_endpoint(endpoint, params=None):
    """Prueba un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nProbando: {url}")
    if params:
        print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response (primeros 500 chars):")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            return data
        else:
            print(f"Error: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

# Probar diferentes endpoints comunes
print("=" * 60)
print("PRUEBA DE ENDPOINTS BESOCCER")
print("=" * 60)

# Endpoint 1: Competitions/Leagues
test_endpoint("/competitions")
test_endpoint("/leagues")
test_endpoint("/competitions", {"country": "Colombia"})
test_endpoint("/leagues", {"country": "Colombia"})

# Endpoint 2: Teams
test_endpoint("/teams")

# Endpoint 3: Matches
test_endpoint("/matches")
test_endpoint("/matches/coming")
test_endpoint("/matches/live")

# Endpoint 4: Standings
test_endpoint("/standings")

# Endpoint 5: Stats
test_endpoint("/stats")

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS")
print("=" * 60)

