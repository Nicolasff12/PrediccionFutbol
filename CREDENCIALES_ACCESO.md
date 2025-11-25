# Credenciales de Acceso - Predicción Fútbol

## 🔐 Usuarios Disponibles

### Usuario Demo (Recomendado)
- **Usuario**: `demo`
- **Contraseña**: `demo123`
- **Email**: demo@test.com

### Usuario Admin
- **Usuario**: `admin`
- **Contraseña**: (verificar con `python manage.py changepassword admin`)
- **Email**: admin@test.com

### Usuario Test
- **Usuario**: `testuser`
- **Contraseña**: (verificar con `python manage.py changepassword testuser`)
- **Email**: test@test.com

## 🌐 URLs de Acceso

### Servidor Local
- **Home**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/auth/login/
- **Registro**: http://127.0.0.1:8000/auth/registro/
- **API Home Data**: http://127.0.0.1:8000/partidos/api/home-data/

## 📝 Crear Nuevo Usuario

### Opción 1: Desde la Web
1. Ir a http://127.0.0.1:8000/auth/registro/
2. Completar el formulario de registro
3. Iniciar sesión con las credenciales creadas

### Opción 2: Desde la Terminal
```bash
python manage.py createsuperuser
```

### Opción 3: Crear Usuario de Prueba
```bash
python manage.py shell
```
```python
from apps.autenticacion.models import Usuario
user = Usuario.objects.create_user(
    username='nuevo_usuario',
    email='nuevo@test.com',
    password='tu_contraseña'
)
```

## 🔄 Cambiar Contraseña

```bash
python manage.py changepassword <username>
```

## 📊 Datos de Prueba

Para poblar la base de datos con datos de prueba (ligas, equipos, partidos):

```bash
python manage.py poblar_datos_prueba
```

Esto creará:
- 1 Liga (Liga BetPlay Dimayor)
- 8 Equipos colombianos
- Partidos próximos y finalizados

## ⚠️ Notas Importantes

1. **Primera vez**: Si es la primera vez que accedes, es recomendable:
   - Crear un usuario desde el registro
   - O usar el usuario `demo` con contraseña `demo123`

2. **Datos vacíos**: Si no ves datos en el home:
   - Ejecuta `python manage.py poblar_datos_prueba` para crear datos de prueba
   - O sincroniza partidos desde la API (botón "Sincronizar Partidos")

3. **API Limitada**: La API de BeSoccer tiene un plan limitado, por lo que algunos datos pueden no estar disponibles desde la API externa.

---

**Última actualización**: 25 de noviembre de 2025

