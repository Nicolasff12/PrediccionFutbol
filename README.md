# Predicción Fútbol - Liga BetPlay

Sistema web para realizar predicciones de partidos de fútbol de la Liga BetPlay usando Inteligencia Artificial (Google Gemini) y datos de la API de Besoccer.

## Características

- ✅ Sistema de autenticación (Login, Registro, Perfil)
- ✅ Integración con API de Besoccer para datos de partidos
- ✅ Predicciones con IA usando Google Gemini
- ✅ Visualización de partidos próximos, en vivo y finalizados
- ✅ Estadísticas de predicciones del usuario
- ✅ Estructura MVC (Modelo-Vista-Controlador)
- ✅ Base de datos PostgreSQL
- ✅ Interfaz moderna con Bootstrap 5

## Requisitos

- Python 3.8+
- PostgreSQL
- API Key de Besoccer
- API Key de Google Gemini

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd PrediccionFutbol
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DB_NAME=prediccion_futbol
DB_USER=postgres
DB_PASSWORD=tu-password-postgres
DB_HOST=localhost
DB_PORT=5432
BESOCCER_API_KEY=tu-api-key-besoccer
GEMINI_API_KEY=tu-api-key-gemini
```

5. Crear la base de datos PostgreSQL:
```sql
CREATE DATABASE prediccion_futbol;
```

6. Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Crear superusuario (opcional):
```bash
python manage.py createsuperuser
```

8. Ejecutar el servidor:
```bash
python manage.py runserver
```

## Estructura del Proyecto

```
PrediccionFutbol/
├── apps/
│   ├── autenticacion/      # App de autenticación
│   │   ├── models.py        # Modelo Usuario
│   │   ├── views.py         # Vistas (Login, Registro, Perfil)
│   │   ├── forms.py         # Formularios
│   │   └── urls.py
│   ├── partidos/            # App de partidos
│   │   ├── models.py        # Modelos (Equipo, Liga, Partido)
│   │   ├── views.py         # Vistas
│   │   ├── controllers/     # Controladores (Lógica de negocio)
│   │   │   └── partido_controller.py
│   │   ├── services/        # Servicios (Integración con APIs)
│   │   │   └── besoccer_service.py
│   │   └── urls.py
│   └── predicciones/        # App de predicciones
│       ├── models.py        # Modelo Prediccion
│       ├── views.py         # Vistas
│       ├── controllers/     # Controladores
│       │   └── prediccion_controller.py
│       ├── services/        # Servicios
│       │   └── gemini_service.py
│       └── urls.py
├── templates/               # Templates HTML
├── static/                 # Archivos estáticos
├── prediccion_futbol/      # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Uso

1. **Registro/Login**: Accede a `/login` o `/registro` para crear una cuenta o iniciar sesión.

2. **Home**: En la página principal verás:
   - Estadísticas generales de la liga
   - Partidos de hoy
   - Próximos partidos
   - Partidos recientes

3. **Sincronizar Partidos**: Haz clic en "Sincronizar Partidos" para obtener los últimos datos de la API de Besoccer.

4. **Crear Predicción**: 
   - Haz clic en "Predecir" en cualquier partido
   - Elige entre predicción con IA o manual
   - La IA analizará el partido y generará una predicción

5. **Mis Predicciones**: Ve a "Mis Predicciones" para ver tu historial y estadísticas.

## Notas

- Asegúrate de tener las API keys configuradas correctamente en el archivo `.env`
- La API de Besoccer puede requerir autenticación específica, ajusta el servicio según sea necesario
- Las predicciones se verifican automáticamente cuando un partido finaliza

## Tecnologías

- Django 4.2
- PostgreSQL
- Bootstrap 5
- Google Gemini AI
- Besoccer API
- Crispy Forms

## Licencia

Este proyecto es de uso educativo.

