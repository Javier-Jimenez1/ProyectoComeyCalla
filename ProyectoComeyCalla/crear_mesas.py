import os
import sys

# Añadir la ruta raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoComeyCalla.settings')

import django
django.setup()

from restauranteapp.models import Mesa

# Crear 10 mesas con capacidad 4 y estado 'Libre'
for i in range(1, 11):
    Mesa.objects.create(numero=i, capacidad=4, estado='Libre')
    print(f"Mesa creada: número {i}, capacidad 4, estado Libre")
