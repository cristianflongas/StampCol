from django.core.management.base import BaseCommand
from django.core.files import File
from customizer.models import ProductOption, DesignAsset
import os

class Command(BaseCommand):
    help = 'Carga datos iniciales de prueba para StampCol (colores, tallas, telas)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Inicializando catálogo de StampCol...'))

        # 1. Colores oficiales de la colección (Negro, Blanco, Azul, Rojo, Amarillo, Rosado, Morado, Naranja)
        colors = [
            {'name': 'Negro', 'code_hex': '#121212', 'description': 'Tono clásico, elegante y versátil', 'order': 1},
            {'name': 'Blanco', 'code_hex': '#FFFFFF', 'description': 'Base clásica, limpia y luminosa', 'order': 2},
            {'name': 'Azul', 'code_hex': '#1D4ED8', 'description': 'Tono clásico y versátil', 'order': 3},
            {'name': 'Rojo', 'code_hex': '#DC2626', 'description': 'Vibrante y de alto impacto', 'order': 4},
            {'name': 'Amarillo', 'code_hex': '#FACC15', 'description': 'Enérgico y creativo', 'order': 5},
            {'name': 'Rosado', 'code_hex': '#F472B6', 'description': 'Tono moderno y fresco', 'order': 6},
            {'name': 'Morado', 'code_hex': '#7C3AED', 'description': 'Elegante y artístico', 'order': 7},
            {'name': 'Naranja', 'code_hex': '#EA580C', 'description': 'Streetwear dinámico', 'order': 8},
        ]

        for c in colors:
            ProductOption.objects.get_or_create(
                option_type='COLOR',
                name=c['name'],
                defaults={
                    'code_hex': c['code_hex'],
                    'description': c['description'],
                    'display_order': c['order']
                }
            )

        # 2. Tallas
        sizes = [
            {'name': 'S', 'desc': 'Pequeña (Ancho 51cm / Largo 66cm)', 'order': 1},
            {'name': 'M', 'desc': 'Mediana (Ancho 55cm / Largo 69cm)', 'order': 2},
            {'name': 'L', 'desc': 'Grande (Ancho 59cm / Largo 72cm)', 'order': 3},
            {'name': 'XL', 'desc': 'Extra Grande (Ancho 63cm / Largo 75cm)', 'order': 4},
            {'name': 'Oversize', 'desc': 'Corte holgado streetwear', 'order': 5},
        ]

        for s in sizes:
            ProductOption.objects.get_or_create(
                option_type='SIZE',
                name=s['name'],
                defaults={'description': s['desc'], 'display_order': s['order']}
            )

        # 3. Telas para Camisetas Básicas
        fabrics = [
            {'name': '100% Algodón Peinado 180g', 'desc': 'Fresca, suave al tacto y de alta durabilidad', 'order': 1},
            {'name': 'Algodón Pesado Streetwear 220g', 'desc': 'Estructura premium con caída firme', 'order': 2},
        ]

        for f in fabrics:
            ProductOption.objects.get_or_create(
                option_type='FABRIC',
                name=f['name'],
                defaults={'description': f['desc'], 'extra_price': 0, 'display_order': f['order']}
            )

        self.stdout.write(self.style.SUCCESS('¡Catálogo inicial de StampCol cargado exitosamente!'))
