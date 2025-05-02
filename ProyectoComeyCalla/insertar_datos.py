import os
import sys

# Añadir la ruta raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoComeyCalla.settings')

import django
django.setup()

from restauranteapp.models import Plato

platos_carta = [
    # Tapas
    {
        "nombre": "Jamón Iberico",
        "descripcion": "Lonchas finas de bellota, con pan con tomate",
        "precio": 4.00,
        "tipo": "tapa",
    },
    {
        "nombre": "Patatas Bravas",
        "descripcion": "Salsa picante y alioli",
        "precio": 3.75,
        "tipo": "tapa"
    },
    {
        "nombre": "Croquetas",
        "descripcion": "De jamón, bacalao y espinacas",
        "precio": 3.75,
        "tipo": "tapa",
    },
    {
        "nombre": "Gazpacho Andaluz",
        "descripcion": "Fresco, con picatostes aparte",
        "precio": 3.25,
        "tipo": "tapa",
    },
    {
        "nombre": "Ensaladilla Rusa",
        "descripcion": "Con atún y huevo",
        "precio": 3.75,
        "tipo": "tapa",
    },
    {
        "nombre": "Ensalada Mixta",
        "descripcion": "Lechuga, tomate, maíz, atún",
        "precio": 3.75,
        "tipo": "tapa"
    },
    {
        "nombre": "Tortilla Española",
        "descripcion": "Tradicional (con cebolla) y variante sin gluten",
        "precio": 4.75,
        "tipo": "tapa",
    },
    {
        "nombre": "Pimientos Asados",
        "descripcion": "Con sal marina",
        "precio": 3.00,
        "tipo": "tapa"
    },

    # Platos principales
    {
        "nombre": "Paella Valenciana",
        "descripcion": "Arroz con pollo, conejo y verduras",
        "precio": 12.00,
        "tipo": "principal"
    },
    {
        "nombre": "Pulpo a la Gallega",
        "descripcion": "Con patata y pimentón",
        "precio": 10.00,
        "tipo": "principal"
    },
    {
        "nombre": "Cocido Madrileño",
        "descripcion": "Servido en 3 vuelcos: sopa, garbanzos, carnes",
        "precio": 8.00,
        "tipo": "principal"
    },
    {
        "nombre": "Pescaito Frito",
        "descripcion": "Boquerones, calamares y cazón en adobo",
        "precio": 15.00,
        "tipo": "principal"
    },

    # Bebidas
    {
        "nombre": "Agua",
        "descripcion": "Agua",
        "precio": 1.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Coca-Cola",
        "descripcion": "Coca-Cola",
        "precio": 1.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Fanta",
        "descripcion": "Fanta",
        "precio": 1.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Sprite",
        "descripcion": "Sprite",
        "precio": 1.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Aquarius",
        "descripcion": "Aquarius",
        "precio": 1.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Cruz Campo",
        "descripcion": "Con y sin alcohol",
        "precio": 2.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Estrella Galicia",
        "descripcion": "Con y sin alcohol",
        "precio": 2.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Estrella del sur",
        "descripcion": "Con y sin alcohol",
        "precio": 2.50,
        "tipo": "bebida"
    },
    {
        "nombre": "Rioja",
        "descripcion": "Rioja",
        "precio": 3.00,
        "tipo": "bebida"
    },
    {
        "nombre": "Ribera del Duero",
        "descripcion": "Ribera del Duero",
        "precio": 3.00,
        "tipo": "bebida"
    },
    {
        "nombre": "Blanco Verdejo",
        "descripcion": "Blanco Verdejo",
        "precio": 3.00,
        "tipo": "bebida"
    },
    {
        "nombre": "Sangria",
        "descripcion": "Tradicional y sin alcohol",
        "precio": 6.00,
        "tipo": "bebida"
    },

    # Postres
    {
        "nombre": "Crema Catalana",
        "descripcion": "Crema de yema con azúcar caramelizado",
        "precio": 4.50,
        "tipo": "postre"
    },
    {
        "nombre": "Torrijas",
        "descripcion": "Pan frito con leche y miel",
        "precio": 6.00,
        "tipo": "postre"
    },
    {
        "nombre": "Helado de Turrón",
        "descripcion": "Casero, con trozos de almendra",
        "precio": 3.00,
        "tipo": "postre"
    }
]

for plato in platos_carta :
    Plato.objects.create(**plato)
    print(f"Plato creado: {plato['nombre']}")
