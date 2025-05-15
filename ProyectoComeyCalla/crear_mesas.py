from django.core.management.base import BaseCommand
from restauranteapp.models import Mesa

class Command(BaseCommand):
    help = 'Crear 10 mesas predeterminadas'

    def handle(self, *args, **kwargs):
        for i in range(1, 11):
            mesa, created = Mesa.objects.get_or_create(numero=i, defaults={'capacidad': 4, 'estado': 'Libre'})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Mesa {i} creada'))
            else:
                self.stdout.write(f'Mesa {i} ya existía')
