# 🚀 Guía de Despliegue - Predicción Fútbol

Esta guía te ayudará a desplegar tu proyecto Django de forma fácil y rápida.

## 📊 Comparación de Plataformas

| Plataforma | Dificultad | Gratis | Mejor Para |
|------------|-----------|--------|------------|
| **Railway** ⭐ | ⭐ Muy Fácil | ✅ Sí | Django (Recomendado) |
| **Render** | ⭐⭐ Fácil | ✅ Sí (90 días) | Django |
| **Fly.io** | ⭐⭐ Fácil | ✅ Sí | Django |
| **Vercel** | ⭐⭐⭐ Media | ✅ Sí | No ideal para Django |
| **Heroku** | ⭐⭐ Fácil | ❌ No | Django (Pago) |

---

## 🏆 OPCIÓN 1: Railway (RECOMENDADO - MÁS FÁCIL)

Railway es la opción más fácil y recomendada para Django.

### Pasos:

1. **Crear cuenta en Railway**
   - Ve a https://railway.app
   - Inicia sesión con GitHub

2. **Crear nuevo proyecto**
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta tu repositorio

3. **Configurar Base de Datos PostgreSQL**
   - En tu proyecto, click en "+ New"
   - Selecciona "Database" → "Add PostgreSQL"
   - Railway creará automáticamente la base de datos

4. **Configurar Variables de Entorno**
   - En tu proyecto, ve a "Variables"
   - Agrega las siguientes variables:

```bash
SECRET_KEY=tu-secret-key-generada
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost
USE_POSTGRES=True
DB_NAME=${{Postgres.DATABASE}}
DB_USER=${{Postgres.USER}}
DB_PASSWORD=${{Postgres.PASSWORD}}
DB_HOST=${{Postgres.HOST}}
DB_PORT=${{Postgres.PORT}}
BESOCCER_API_KEY=tu-api-key-besoccer
GEMINI_API_KEY=tu-api-key-gemini
```

**Nota:** Las variables `${{Postgres.*}}` se llenan automáticamente si conectaste la base de datos.

5. **Configurar Build Settings**
   - Railway detectará automáticamente Django
   - Si no, configura:
     - **Build Command:** `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
     - **Start Command:** `python manage.py runserver 0.0.0.0:$PORT`

6. **Desplegar**
   - Railway desplegará automáticamente
   - Obtendrás una URL como: `tu-proyecto.railway.app`

### Generar SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### ✅ Ventajas de Railway:
- ✅ Muy fácil de usar
- ✅ PostgreSQL incluido gratis
- ✅ $5 de crédito mensual gratis
- ✅ Despliegue automático desde GitHub
- ✅ Logs en tiempo real
- ✅ Dominio personalizado gratis

---

## 🎯 OPCIÓN 2: Render (FÁCIL Y GRATIS)

Render es otra excelente opción gratuita.

### Pasos:

1. **Crear cuenta en Render**
   - Ve a https://render.com
   - Inicia sesión con GitHub

2. **Crear Base de Datos PostgreSQL**
   - Click en "New +" → "PostgreSQL"
   - Nombre: `prediccion-futbol-db`
   - Plan: Free
   - Click "Create Database"
   - **Guarda las credenciales** (host, database, user, password, port)

3. **Crear Web Service**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Configuración:
     - **Name:** `prediccion-futbol`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
     - **Start Command:** `gunicorn prediccion_futbol.wsgi:application`

4. **Configurar Variables de Entorno**
   - En tu Web Service, ve a "Environment"
   - Agrega:

```bash
SECRET_KEY=tu-secret-key-generada
DEBUG=False
ALLOWED_HOSTS=tu-proyecto.onrender.com,localhost
USE_POSTGRES=True
DB_NAME=nombre_de_tu_db
DB_USER=usuario_de_tu_db
DB_PASSWORD=password_de_tu_db
DB_HOST=dpg-xxxxx-a.oregon-postgres.render.com
DB_PORT=5432
BESOCCER_API_KEY=tu-api-key-besoccer
GEMINI_API_KEY=tu-api-key-gemini
```

5. **Instalar Gunicorn**
   - Agrega a `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```

6. **Desplegar**
   - Render desplegará automáticamente
   - URL: `tu-proyecto.onrender.com`

### ✅ Ventajas de Render:
- ✅ Gratis (90 días, luego $7/mes)
- ✅ PostgreSQL incluido
- ✅ Muy estable
- ✅ SSL automático

---

## 🚁 OPCIÓN 3: Fly.io (GRATIS Y RÁPIDO)

Fly.io es excelente para aplicaciones Django.

### Pasos:

1. **Instalar Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Iniciar sesión**
   ```bash
   fly auth login
   ```

3. **Inicializar proyecto**
   ```bash
   fly launch
   ```
   - Te preguntará sobre la configuración
   - Selecciona región cercana
   - No crees PostgreSQL todavía

4. **Crear Base de Datos**
   ```bash
   fly postgres create --name prediccion-futbol-db
   ```
   - Guarda las credenciales

5. **Conectar Base de Datos**
   ```bash
   fly postgres attach prediccion-futbol-db
   ```

6. **Configurar Variables de Entorno**
   ```bash
   fly secrets set SECRET_KEY="tu-secret-key"
   fly secrets set DEBUG="False"
   fly secrets set ALLOWED_HOSTS="tu-proyecto.fly.dev,localhost"
   fly secrets set USE_POSTGRES="True"
   fly secrets set DB_NAME="nombre_db"
   fly secrets set DB_USER="usuario"
   fly secrets set DB_PASSWORD="password"
   fly secrets set DB_HOST="host.flycast"
   fly secrets set DB_PORT="5432"
   fly secrets set BESOCCER_API_KEY="tu-api-key"
   fly secrets set GEMINI_API_KEY="tu-api-key"
   ```

7. **Desplegar**
   ```bash
   fly deploy
   ```

### ✅ Ventajas de Fly.io:
- ✅ Gratis con límites generosos
- ✅ Muy rápido
- ✅ Global edge network
- ✅ PostgreSQL incluido

---

## 📝 Preparar el Proyecto para Despliegue

### 1. Verificar requirements.txt

Asegúrate de tener todas las dependencias:

```txt
Django==4.2.7
psycopg2-binary>=2.9.9
python-decouple==3.8
requests==2.31.0
google-generativeai==0.3.1
Pillow>=10.0.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
whitenoise==6.6.0
gunicorn==21.2.0
```

### 2. Crear archivo Procfile (para Render/Fly.io)

Crea un archivo `Procfile` en la raíz:

```
web: gunicorn prediccion_futbol.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. Verificar settings.py

Asegúrate de que `settings.py` tenga:

```python
import os
from decouple import config

# Base de datos
USE_POSTGRES = config('USE_POSTGRES', default=False, cast=bool)

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default=5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Middleware
MIDDLEWARE = [
    # ... otros middlewares
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... resto
]
```

### 4. Crear .gitignore

Asegúrate de tener `.gitignore`:

```
*.pyc
__pycache__/
db.sqlite3
.env
venv/
staticfiles/
*.log
```

---

## 🎯 Recomendación Final

**Para empezar rápido:** Usa **Railway** ⭐
- Es la más fácil
- Configuración automática
- PostgreSQL incluido
- Despliegue en minutos

**Para producción:** Usa **Render** o **Fly.io**
- Más control
- Mejor rendimiento
- Más opciones de configuración

---

## 🔧 Solución de Problemas Comunes

### Error: "No module named 'psycopg2'"
```bash
# Agrega a requirements.txt:
psycopg2-binary>=2.9.9
```

### Error: "Static files not found"
```bash
# Ejecuta localmente:
python manage.py collectstatic
```

### Error: "Database connection failed"
- Verifica las variables de entorno
- Asegúrate de que la base de datos permita conexiones externas
- Verifica el host y puerto

### Error: "ALLOWED_HOSTS"
- Agrega tu dominio a `ALLOWED_HOSTS`
- Formato: `tu-proyecto.railway.app` o `tu-proyecto.onrender.com`

---

## 📚 Recursos Adicionales

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Fly.io Docs:** https://fly.io/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/

---

## ✅ Checklist de Despliegue

- [ ] Cuenta creada en la plataforma elegida
- [ ] Repositorio conectado
- [ ] Base de datos PostgreSQL creada
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generada y configurada
- [ ] requirements.txt actualizado
- [ ] Migraciones ejecutadas
- [ ] Static files configurados
- [ ] ALLOWED_HOSTS configurado
- [ ] Despliegue exitoso
- [ ] Aplicación funcionando

¡Listo! Tu aplicación debería estar funcionando en producción. 🎉

