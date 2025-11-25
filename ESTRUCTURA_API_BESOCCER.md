# Estructura Correcta de la API de BeSoccer

## 📋 Resumen

La API de BeSoccer usa una estructura basada en **`method`** en lugar de `req`, y requiere tanto `key` como `token` en algunos casos.

## 🔧 Estructura de la API

### URL Base
```
https://apiclient.besoccerapps.com/scripts/api/api.php
```

### Parámetros Base
- `key`: API key (requerido)
- `token`: Token adicional (opcional, puede ser requerido según el plan)
- `format`: `json` (requerido)
- `method`: Método de la API (ej: `matches.next`, `standings`, `team.stats`)

### Ejemplo de Request
```bash
curl "https://apiclient.besoccerapps.com/scripts/api/api.php?key=TU_KEY&token=TU_TOKEN&format=json&method=matches.next&competition=colombia_primera_a&limit=10"
```

## 📝 Métodos Disponibles

### 1. Próximos Partidos
```python
method = "matches.next"
params = {
    "competition": "colombia_primera_a",
    "limit": 10
}
```

### 2. Tabla de Posiciones
```python
method = "standings"
params = {
    "competition": "colombia_primera_a"
}
```

### 3. Estadísticas de Equipo
```python
method = "team.stats"
params = {
    "team": team_id
}
```

### 4. Últimos Partidos de un Equipo
```python
method = "matches.team"
params = {
    "team": team_id,
    "limit": 10
}
```

### 5. Equipos de una Liga
```python
# Método antiguo que funciona con el plan actual
req = "teams"
params = {
    "league": 1
}
```

## ⚠️ Limitaciones del Plan Actual

El plan actual de la API key (`fbe606a6eda33a3a249cfdb242d4f163`) tiene limitaciones:

### ✅ Disponible:
- `req=teams` con `league=1` - Obtiene equipos (método antiguo)

### ❌ No Disponible (requiere plan superior):
- `method=matches.next` - Próximos partidos
- `method=standings` - Tabla de posiciones
- `method=team.stats` - Estadísticas de equipo
- `method=matches.team` - Partidos de equipo

## 🔑 Configuración

### Variables de Entorno

Agregar en `.env` o `settings.py`:

```python
BESOCCER_API_KEY = "fbe606a6eda33a3a249cfdb242d4f163"
BESOCCER_TOKEN = ""  # Token adicional si es requerido
```

### Uso en el Servicio

El servicio `BesoccerService` ahora:
1. Intenta usar la estructura nueva (`method`) cuando es posible
2. Usa el método antiguo (`req=teams`) como fallback para equipos
3. Maneja errores cuando los métodos no están disponibles

## 📧 Para Obtener Más Funcionalidades

Contactar a **api@besoccer.com** para:
1. Verificar qué métodos están disponibles con el plan actual
2. Solicitar upgrade del plan si se necesitan más funcionalidades
3. Obtener el `token` si es requerido para tu plan

## 🛠️ Código Implementado

El servicio está actualizado para:
- ✅ Usar `method` en lugar de `req` cuando es posible
- ✅ Mantener compatibilidad con el método antiguo que funciona
- ✅ Manejar errores cuando los métodos no están disponibles
- ✅ Intentar ambos formatos para máxima compatibilidad

---

**Última actualización**: 25 de noviembre de 2025
**Estado**: ✅ Estructura correcta implementada, ⚠️ Plan limitado - solo `teams` disponible

