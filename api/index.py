"""
Vercel serverless handler for Django
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prediccion_futbol.settings')

# Import Django
import django
django.setup()

# Import WSGI application
from prediccion_futbol.wsgi import application

# Export for Vercel
def handler(request):
    return application

