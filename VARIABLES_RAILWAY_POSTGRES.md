# Variables de Entorno para Railway con PostgreSQL

## 📋 Variables que DEBES configurar en Railway

Configura estas variables en **Railway → Tu Proyecto → Variables**:

```env
USE_POSTGRES=True
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=JaKYDWwYpghIhqQdFSFoJmWIMYakurQD
DB_HOST=postgres.railway.internal
DB_PORT=5432
```

## ⚠️ IMPORTANTE

1. **NO pongas comillas** alrededor de los valores (a menos que el valor tenga espacios)
2. **USE_POSTGRES** debe ser exactamente `True` (sin comillas)
3. **DB_HOST** debe ser `postgres.railway.internal` (la URL interna de Railway)
4. **DB_NAME** debe ser `railway` (el nombre de tu base de datos en Railway)

## 🔄 Cómo se crean las tablas automáticamente

Railway ejecutará las migraciones en dos momentos:

1. **Comando `release`** (en el `Procfile`): Se ejecuta ANTES de iniciar el servidor
   ```
   release: python manage.py migrate --noinput
   ```

2. **Script `start.sh`**: También ejecuta migraciones como respaldo
   ```bash
   python manage.py migrate --noinput
   ```

## ✅ Pasos para desplegar

1. **Configura las variables** en Railway (arriba)
2. **Haz commit y push** de tus cambios:
   ```bash
   git add .
   git commit -m "Configuración PostgreSQL para Railway"
   git push
   ```
3. **Railway desplegará automáticamente** y ejecutará las migraciones
4. **Revisa los logs** en Railway para verificar que las migraciones se ejecutaron correctamente

## 🔍 Verificar que funcionó

En los logs de Railway deberías ver:
```
Ejecutando migraciones...
Operations to perform:
  Apply all migrations: admin, auth, autenticacion, contenttypes, partidos, sessions
Running migrations:
  Applying autenticacion.0001_initial... OK
  Applying partidos.0001_initial... OK
  ...
```

## 🐛 Si hay problemas

- Verifica que todas las variables estén configuradas correctamente
- Revisa los logs de Railway para ver errores específicos
- Asegúrate de que el servicio PostgreSQL esté conectado a tu proyecto en Railway

