"""
Script para probar diferentes variaciones de la API de BeSoccer
"""
import requests
import json

API_KEY = "fbe606a6eda33a3a249cfdb242d4f163"

# Diferentes formatos de URL base
BASE_URLS = [
    "https://api.besoccer.com",
    "https://api.besoccer.com/v1",
    "https://api.besoccer.com/api",
    "https://api.besoccer.com/api/v1",
    "https://besoccer.com/api",
]

# Diferentes formatos de autenticación
AUTH_FORMATS = [
    {"Authorization": f"Bearer {API_KEY}"},
    {"Authorization": f"Token {API_KEY}"},
    {"X-API-Key": API_KEY},
    {"api_key": API_KEY},
    {"key": API_KEY},
]

# Endpoints a probar
ENDPOINTS = [
    "/competitions",
    "/leagues",
    "/matches",
    "/teams",
    "/standings",
]

def test_combination(base_url, headers, endpoint):
    """Prueba una combinación específica"""
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 404:
            print(f"\n[ENCONTRADO] Status {response.status_code}")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
            except:
                print(f"Response (text): {response.text[:300]}")
            return True
    except Exception as e:
        pass
    return False

print("=" * 60)
print("PROBANDO DIFERENTES COMBINACIONES DE API BESOCCER")
print("=" * 60)

found = False
for base_url in BASE_URLS:
    for auth_format in AUTH_FORMATS:
        headers = {
            **auth_format,
            'Content-Type': 'application/json'
        }
        for endpoint in ENDPOINTS:
            if test_combination(base_url, headers, endpoint):
                found = True
                break
        if found:
            break
    if found:
        break

if not found:
    print("\n[INFO] No se encontraron endpoints válidos con las combinaciones probadas.")
    print("Puede que la API de BeSoccer:")
    print("1. Use una URL base diferente")
    print("2. Requiera un formato de autenticación específico")
    print("3. Necesite parámetros obligatorios en la URL")
    print("\nSugerencia: Revisar la documentación oficial de BeSoccer API")

print("\n" + "=" * 60)

