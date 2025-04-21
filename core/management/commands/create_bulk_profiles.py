import random
from datetime import date
from django.core.management.base import BaseCommand
from core.models import Profile

class Command(BaseCommand):
    help = 'Create bulk profiles for testing'

    def handle(self, *args, **kwargs):
        for i in range(1, 81):
            Profile.objects.create(
                rut=i,
                first_name=f'FirstName{i}',
                last_name=f'LastName{i}',
                phone=random.randint(1000000000, 9999999999),
                email=f'user{i}@example.com',
                Transportista=f'Transportista{i}',
                CodTransportista=i,
                status='Baja',
                present=False,
                assigned=False,
                Patente=f'ABC{i}',
                active=True
            )
        self.stdout.write(self.style.SUCCESS('Successfully created 80 profiles'))
