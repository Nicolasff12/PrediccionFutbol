# Variables de Entorno para Railway - Configuración Completa

Copia y pega estas variables en Railway → Tu Proyecto → Variables → Raw Editor

## 🔐 Variables de Seguridad (OBLIGATORIAS)

```env
SECRET_KEY=django-insecure-cambiar-esta-clave-en-produccion-genera-una-nueva
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://web-production-7171.up.railway.app
```

**⚠️ IMPORTANTE:**
- **SECRET_KEY**: Genera una nueva clave secreta ejecutando:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- **CSRF_TRUSTED_ORIGINS**: Reemplaza `web-production-7171.up.railway.app` con tu dominio real de Railway

---

## 🗄️ Variables de Base de Datos PostgreSQL

```env
USE_POSTGRES=True
DB_NAME=${{Postgres.DATABASE}}
DB_USER=${{Postgres.USER}}
DB_PASSWORD=${{Postgres.PASSWORD}}
DB_HOST=${{Postgres.HOST}}
DB_PORT=${{Postgres.PORT}}
```

**📝 Nota:** Las variables `${{Postgres.*}}` se resuelven automáticamente si tienes el servicio PostgreSQL conectado en Railway.

---

## 🔑 Variables de APIs

```env
BESOCCER_API_KEY=fbe606a6eda33a3a249cfdb242d4f163
GEMINI_API_KEY=AIzaSyDizbSmH5i5X6gHxOwCxr6vtEVsztlXLQE
```

---

## 📋 Formato para Copiar y Pegar en Railway

Copia todo este bloque y pégalo en el Raw Editor de Railway:

```env
SECRET_KEY=django-insecure-cambiar-esta-clave-en-produccion-genera-una-nueva
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

---

## ✅ Pasos para Configurar en Railway

1. **Ve a tu proyecto en Railway**
   - Abre tu proyecto → Settings → Variables

2. **Abre el Raw Editor**
   - Click en "Raw Editor" (pestaña ENV)

3. **Pega las variables**
   - Copia el bloque completo de arriba
   - Pégalo en el editor
   - **Reemplaza** `web-production-7171.up.railway.app` con tu dominio real

4. **Genera y reemplaza SECRET_KEY**
   - Ejecuta localmente: 
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - Copia el resultado y reemplaza el valor de `SECRET_KEY`

5. **Click en "Update Variables"**
   - Railway redesplegará automáticamente

---

## 🔍 Verificación

Después de agregar las variables:

1. **Revisa los logs de Railway**
   - Deberías ver: "Ejecutando migraciones..."
   - Las migraciones se ejecutarán automáticamente

2. **Verifica que esté usando PostgreSQL**
   - En los logs NO deberías ver referencias a SQLite
   - Si ves errores de conexión a PostgreSQL, verifica que el servicio esté conectado

3. **Prueba la aplicación**
   - Abre tu URL de Railway
   - Deberías poder registrarte e iniciar sesión

---

## ⚠️ Solución de Problemas

### Error: "no such table"
- **Causa**: Las migraciones no se ejecutaron o está usando SQLite
- **Solución**: 
  1. Verifica que `USE_POSTGRES=True`
  2. Verifica que el servicio PostgreSQL esté conectado
  3. Revisa los logs del comando `release` (debería ejecutar migraciones)

### Error: "CSRF verification failed"
- **Causa**: El dominio no está en `CSRF_TRUSTED_ORIGINS`
- **Solución**: Agrega tu dominio exacto a `CSRF_TRUSTED_ORIGINS`

### Error: "Database connection failed"
- **Causa**: Variables de PostgreSQL incorrectas o servicio no conectado
- **Solución**: 
  1. Verifica que el servicio PostgreSQL esté creado y conectado
  2. Verifica que las variables `${{Postgres.*}}` estén configuradas

---

## 📝 Notas Adicionales

- **SECRET_KEY**: NUNCA compartas esta clave. Es única para tu aplicación.
- **DEBUG**: Mantén en `False` en producción para seguridad
- **ALLOWED_HOSTS**: Puedes agregar dominios personalizados si los tienes
- **CSRF_TRUSTED_ORIGINS**: Debe incluir todos los dominios desde donde se accede a la app

---

## 🎯 Checklist Final

- [ ] SECRET_KEY generada y configurada
- [ ] DEBUG=False configurado
- [ ] ALLOWED_HOSTS configurado
- [ ] CSRF_TRUSTED_ORIGINS con tu dominio real
- [ ] USE_POSTGRES=True configurado
- [ ] Variables de PostgreSQL configuradas (o servicio conectado)
- [ ] BESOCCER_API_KEY configurada
- [ ] GEMINI_API_KEY configurada
- [ ] Servicio PostgreSQL creado y conectado en Railway
- [ ] Variables guardadas y Railway redesplegado
- [ ] Migraciones ejecutadas (revisar logs)

¡Listo! Tu aplicación debería funcionar correctamente. 🚀

