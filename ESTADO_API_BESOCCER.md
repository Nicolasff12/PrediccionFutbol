# Estado de la Integración con BeSoccer API

## 📋 Resumen

Se ha identificado y configurado la estructura correcta de la API de BeSoccer. La API funciona con una estructura basada en query parameters en lugar de endpoints REST.

## ✅ Lo que se ha hecho

1. **API Key agregada**: Configurada en `prediccion_futbol/settings.py`
2. **Estructura correcta identificada**: 
   - Base URL: `http://apiclient.besoccerapps.com/scripts/api/api.php`
   - Método: Query parameters (`key`, `tz`, `format`, `req`)
3. **Servicio actualizado**: `BesoccerService` reescrito completamente con la estructura correcta
4. **Pruebas exitosas**: Se confirmó que `req=teams` funciona correctamente

## ✅ Funcionalidad Confirmada

### Request que funciona:
- ✅ **`req=teams`** con parámetro `league={id}` - Obtiene equipos de una liga
  - Ejemplo: `req=teams&league=1` devuelve 20 equipos correctamente

## ⚠️ Limitaciones del Plan Actual

La API key tiene un **plan limitado** que solo permite ciertos requests. Muchos requests devuelven:

```
"info-not-allowed-request-for-api-account-type. / Petición no permitida para ésta key"
```

### Requests que NO están disponibles con el plan actual:
- ❌ `req=standings` - Tabla de posiciones
- ❌ `req=table` - Tabla de posiciones (alternativa)
- ❌ `req=matches` - Partidos
- ❌ `req=games` - Partidos (alternativa)
- ❌ `req=leagues` - Ligas
- ❌ `req=competitions` - Competiciones (devuelve 500)

### Requests que necesitan verificación:
- ❓ `req=players` - Jugadores
- ❓ `req=top_scorers` - Goleadores
- ❓ `req=team_stats` - Estadísticas de equipo
- ❓ `req=league_stats` - Estadísticas de liga
- ❓ `req=match` - Detalle de partido

## 🔧 Estructura de la API

### URL Base
```
http://apiclient.besoccerapps.com/scripts/api/api.php
```

### Parámetros Base (siempre requeridos)
- `key`: API key
- `tz`: Zona horaria (ej: `America/Bogota`, `Europe/Madrid`)
- `format`: `json`
- `req`: Tipo de request (ej: `teams`, `matches`, `standings`)

### Ejemplo de Request
```bash
curl --location -g 'http://apiclient.besoccerapps.com/scripts/api/api.php?key={APIKEY}&tz=America/Bogota&format=json&req=teams&league=1'
```

### Respuesta de Equipos
```json
{
  "team": [
    {
      "id": "347",
      "id_comp": "6692237",
      "nameShow": "Athletic",
      "nameShowTeam": "Athletic",
      "fullName": "Athletic Club",
      "short_name": "ATH",
      "shield": "https://cdn.resfu.com/img_data/equipos/347.png?size=60x&lossy=1",
      "shield_big": "https://cdn.resfu.com/img_data/equipos/347.png?size=200x&lossy=1",
      ...
    }
  ]
}
```

## 📝 Próximos Pasos

### 1. Verificar Plan de API

Contactar a **api@besoccer.com** para:
- Verificar qué requests están disponibles con el plan actual
- Solicitar upgrade del plan si se necesitan más funcionalidades
- Obtener documentación completa de requests disponibles

### 2. Implementar Soluciones Alternativas

Para los datos que no están disponibles con el plan actual:

1. **Datos de partidos**: 
   - Usar datos almacenados localmente en la base de datos
   - Implementar sincronización manual o con otra fuente

2. **Tabla de posiciones**:
   - Calcular desde los partidos almacenados localmente
   - Usar datos de otra API complementaria

3. **Estadísticas**:
   - Calcular desde datos locales
   - Combinar con datos de otras fuentes

## 🛠️ Código Implementado

### Servicio Actualizado
- ✅ `BesoccerService` con estructura correcta
- ✅ Manejo de errores mejorado
- ✅ Detección de limitaciones del plan
- ✅ Métodos preparados para cuando se habilite el plan completo

### Métodos Disponibles
- ✅ `obtener_equipos_liga(liga_id)` - **FUNCIONA**
- ⏳ `obtener_partidos_liga()` - Requiere plan superior
- ⏳ `obtener_tabla_posiciones()` - Requiere plan superior
- ⏳ `obtener_jugadores_equipo()` - Por verificar
- ⏳ Otros métodos - Por verificar

## 📧 Contacto

**Email de soporte BeSoccer**: api@besoccer.com

**Para solicitar**:
- Lista completa de requests disponibles con el plan actual
- Información sobre planes superiores
- Documentación de la API

---

**Última actualización**: 25 de noviembre de 2025
**Estado**: ✅ Estructura correcta identificada, ⚠️ Plan limitado - solo `teams` disponible
