# Variables de Entorno para Railway - Configuración Completa

## Variables Requeridas

Agrega estas variables en Railway → Tu Proyecto → Variables:

### 1. Variables de Seguridad (OBLIGATORIAS)

```
SECRET_KEY=tu-secret-key-generada-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://web-production-7171.up.railway.app
```

**Importante:** 
- Genera un SECRET_KEY único: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Reemplaza `web-production-7171.up.railway.app` con tu dominio real de Railway

### 2. Variables de Base de Datos PostgreSQL

```
USE_POSTGRES=True
DB_NAME=${{Postgres.DATABASE}}
DB_USER=${{Postgres.USER}}
DB_PASSWORD=${{Postgres.PASSWORD}}
DB_HOST=${{Postgres.HOST}}
DB_PORT=${{Postgres.PORT}}
```

**Nota:** Las variables `${{Postgres.*}}` se resuelven automáticamente si tienes el servicio PostgreSQL conectado.

### 3. Variables de APIs

```
BESOCCER_API_KEY=fbe606a6eda33a3a249cfdb242d4f163
GEMINI_API_KEY=AIzaSyDizbSmH5i5X6gHxOwCxr6vtEVsztlXLQE
```

## Lista Completa para Copiar y Pegar

```
SECRET_KEY=tu-secret-key-generada
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://web-production-7171.up.railway.app
USE_POSTGRES=True
DB_NAME=${{Postgres.DATABASE}}
DB_USER=${{Postgres.USER}}
DB_PASSWORD=${{Postgres.PASSWORD}}
DB_HOST=${{Postgres.HOST}}
DB_PORT=${{Postgres.PORT}}
BESOCCER_API_KEY=fbe606a6eda33a3a249cfdb242d4f163
GEMINI_API_KEY=AIzaSyDizbSmH5i5X6gHxOwCxr6vtEVsztlXLQE
```

## Verificación

Después de agregar las variables:
1. Railway redesplegará automáticamente
2. Revisa los logs para verificar que las migraciones se ejecuten
3. Si ves errores, verifica que el servicio PostgreSQL esté conectado

