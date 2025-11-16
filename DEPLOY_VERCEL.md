# Guía de Despliegue en Vercel

## Configuración en Vercel

### 1. Variables de Entorno

En el dashboard de Vercel, ve a **Settings > Environment Variables** y agrega las siguientes variables:

#### Variables Requeridas:

```
SECRET_KEY=tu-secret-key-django-muy-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.vercel.app,localhost,127.0.0.1
```

#### Variables de Base de Datos (PostgreSQL):

Si usas PostgreSQL en Vercel o una base de datos externa:

```
USE_POSTGRES=True
DB_NAME=nombre_base_datos
DB_USER=usuario_postgres
DB_PASSWORD=contraseña_postgres
DB_HOST=host_postgres
DB_PORT=5432
```

**O si usas SQLite (solo para desarrollo):**

```
USE_POSTGRES=False
```

#### Variables de APIs:

```
BESOCCER_API_KEY=tu-api-key-besoccer
GEMINI_API_KEY=tu-api-key-google-gemini
```

### 2. Configuración del Proyecto

1. **Conecta tu repositorio** a Vercel desde GitHub/GitLab/Bitbucket

2. **Configuración de Build:**
   - **Framework Preset:** Other
   - **Build Command:** `pip install -r requirements-vercel.txt && python manage.py collectstatic --noinput`
   - **Output Directory:** (dejar vacío)
   - **Install Command:** `pip install -r requirements-vercel.txt`

3. **Root Directory:** (dejar vacío o poner `.`)

### 3. Archivos Necesarios

Asegúrate de tener estos archivos en tu repositorio:
- ✅ `vercel.json` (ya creado)
- ✅ `api/index.py` (ya creado)
- ✅ `requirements-vercel.txt` (ya creado)

### 4. Migraciones

Las migraciones se ejecutarán automáticamente si agregas esto al Build Command:

```bash
pip install -r requirements-vercel.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

### 5. Base de Datos

**Opción A: PostgreSQL en Vercel**
- Usa el addon de PostgreSQL de Vercel
- Las credenciales se configuran automáticamente

**Opción B: Base de Datos Externa**
- Usa servicios como:
  - Supabase (gratis)
  - Railway (gratis)
  - ElephantSQL (gratis)
  - Render (gratis)
- Configura las variables de entorno con las credenciales

**Opción C: SQLite (NO RECOMENDADO para producción)**
- Solo para pruebas
- Los datos se perderán en cada deploy

### 6. Secret Key

Genera una nueva SECRET_KEY para producción:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 7. Despliegue

1. Haz push a tu repositorio
2. Vercel detectará los cambios y desplegará automáticamente
3. Revisa los logs en Vercel si hay errores

## Notas Importantes

⚠️ **Limitaciones de Vercel con Django:**
- Vercel tiene un timeout de 10 segundos para funciones serverless
- No es ideal para aplicaciones Django complejas
- Considera usar Railway, Render, o Heroku para mejor rendimiento

✅ **Alternativas Recomendadas:**
- **Railway.app** - Excelente para Django, gratis
- **Render.com** - Gratis con límites
- **Fly.io** - Buena opción
- **Heroku** - Pago pero muy estable

## Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements-vercel.txt` tenga todas las dependencias
- Revisa los logs de build en Vercel

### Error: "Database connection failed"
- Verifica las variables de entorno de la base de datos
- Asegúrate de que la base de datos permita conexiones externas

### Error: "Static files not found"
- Ejecuta `python manage.py collectstatic` antes del deploy
- Verifica que `STATIC_ROOT` esté configurado correctamente

### Error: "ALLOWED_HOSTS"
- Agrega tu dominio de Vercel a `ALLOWED_HOSTS`
- Formato: `tu-proyecto.vercel.app`

