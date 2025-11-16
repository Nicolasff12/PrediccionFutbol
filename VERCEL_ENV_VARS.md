# Variables de Entorno para Vercel

## 📋 Lista de Variables a Configurar en Vercel

Ve a tu proyecto en Vercel → **Settings** → **Environment Variables** y agrega las siguientes:

### 🔐 Variables Obligatorias

```
SECRET_KEY
```
**Valor:** Genera una clave secreta única para producción
**Cómo generar:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Ejemplo:** `django-insecure-xyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz`

---

```
DEBUG
```
**Valor:** `False`
**Descripción:** Desactiva el modo debug en producción

---

```
ALLOWED_HOSTS
```
**Valor:** `tu-proyecto.vercel.app,localhost,127.0.0.1`
**Descripción:** Dominios permitidos (reemplaza `tu-proyecto` con tu nombre de proyecto)
**Ejemplo:** `prediccion-futbol.vercel.app,localhost,127.0.0.1`

---

### 🗄️ Variables de Base de Datos

#### Opción 1: PostgreSQL (Recomendado)

```
USE_POSTGRES
```
**Valor:** `True`

```
DB_NAME
```
**Valor:** Nombre de tu base de datos PostgreSQL
**Ejemplo:** `prediccion_futbol`

```
DB_USER
```
**Valor:** Usuario de PostgreSQL
**Ejemplo:** `postgres`

```
DB_PASSWORD
```
**Valor:** Contraseña de PostgreSQL
**Ejemplo:** `mi_password_seguro_123`

```
DB_HOST
```
**Valor:** Host de PostgreSQL
**Ejemplo:** `db.xxxxx.supabase.co` (si usas Supabase)
**Ejemplo:** `containers-us-west-xxx.railway.app` (si usas Railway)

```
DB_PORT
```
**Valor:** `5432`
**Descripción:** Puerto estándar de PostgreSQL

---

#### Opción 2: SQLite (Solo para pruebas)

```
USE_POSTGRES
```
**Valor:** `False`

⚠️ **Nota:** SQLite no es recomendado para producción en Vercel ya que los datos se perderán.

---

### 🔑 Variables de APIs

```
BESOCCER_API_KEY
```
**Valor:** Tu API key de Besoccer
**Ejemplo:** `tu_api_key_besoccer_aqui`

```
GEMINI_API_KEY
```
**Valor:** Tu API key de Google Gemini
**Ejemplo:** `tu_api_key_gemini_aqui`
**Cómo obtener:** https://makersuite.google.com/app/apikey

---

## 📝 Ejemplo Completo de Configuración

### Para Producción con PostgreSQL:

```
SECRET_KEY=django-insecure-xyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz
DEBUG=False
ALLOWED_HOSTS=prediccion-futbol.vercel.app,localhost,127.0.0.1
USE_POSTGRES=True
DB_NAME=prediccion_futbol
DB_USER=postgres
DB_PASSWORD=mi_password_seguro
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
BESOCCER_API_KEY=tu_api_key_besoccer
GEMINI_API_KEY=tu_api_key_gemini
```

### Para Desarrollo/Pruebas:

```
SECRET_KEY=django-insecure-xyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
USE_POSTGRES=False
BESOCCER_API_KEY=tu_api_key_besoccer
GEMINI_API_KEY=tu_api_key_gemini
```

---

## 🚀 Servicios de Base de Datos Recomendados (Gratis)

### 1. **Supabase** (Recomendado)
- URL: https://supabase.com
- PostgreSQL gratuito
- 500 MB de almacenamiento
- Fácil de configurar

### 2. **Railway**
- URL: https://railway.app
- PostgreSQL gratuito
- $5 de crédito mensual gratis
- Muy fácil de usar

### 3. **Render**
- URL: https://render.com
- PostgreSQL gratuito
- 90 días gratis, luego $7/mes
- Muy estable

### 4. **ElephantSQL**
- URL: https://www.elephantsql.com
- PostgreSQL gratuito
- 20 MB gratis
- Simple y confiable

---

## ⚙️ Configuración en Vercel Dashboard

1. Ve a tu proyecto en Vercel
2. Click en **Settings**
3. Click en **Environment Variables**
4. Agrega cada variable una por una:
   - **Key:** Nombre de la variable (ej: `SECRET_KEY`)
   - **Value:** Valor de la variable
   - **Environment:** Selecciona `Production`, `Preview`, y `Development`
5. Click en **Save**

---

## ✅ Verificación

Después de configurar las variables:

1. Haz un nuevo deploy en Vercel
2. Revisa los logs del build
3. Si hay errores, verifica que todas las variables estén correctamente escritas
4. Accede a tu aplicación en `https://tu-proyecto.vercel.app`

---

## 🔍 Troubleshooting

### Error: "SECRET_KEY not set"
- Verifica que hayas agregado la variable `SECRET_KEY` en Vercel

### Error: "Database connection failed"
- Verifica las credenciales de la base de datos
- Asegúrate de que la base de datos permita conexiones externas
- Verifica que el host sea correcto

### Error: "ALLOWED_HOSTS"
- Agrega tu dominio de Vercel a `ALLOWED_HOSTS`
- Formato: `tu-proyecto.vercel.app`

### Error: "Static files not found"
- Ejecuta `python manage.py collectstatic` localmente
- Sube la carpeta `staticfiles` al repositorio
- O configura un servicio de almacenamiento de archivos estáticos

