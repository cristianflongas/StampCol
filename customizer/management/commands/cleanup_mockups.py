from django.core.management.base import BaseCommand
from customizer.cleanup import (
    purge_all_mockup_files,
    auto_cleanup_viewed_and_expired_mockups,
    get_mockups_storage_stats,
)

class Command(BaseCommand):
    help = 'Limpia y purga mockups de pedidos para optimizar el almacenamiento del servidor.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Elimina absolutamente todos los archivos de mockups existentes hasta el momento.'
        )
        parser.add_argument(
            '--viewed',
            action='store_true',
            help='Elimina inmediatamente los mockups de los pedidos que ya fueron visualizados.'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Horas máximas de retención para mockups no visualizados (default: 24).'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Muestra el estado actual del almacenamiento de mockups sin borrar nada.'
        )

    def handle(self, *args, **options):
        if options['stats']:
            stats = get_mockups_storage_stats()
            self.stdout.write(self.style.SUCCESS("--- Estado del Almacenamiento de Mockups ---"))
            self.stdout.write(f"Archivos en disco: {stats['total_files']}")
            self.stdout.write(f"Espacio utilizado: {stats['total_mb']} MB ({stats['total_bytes']} bytes)")
            self.stdout.write(f"Total pedidos en BD: {stats['total_orders']}")
            self.stdout.write(f"Pedidos visualizados: {stats['viewed_orders']}")
            self.stdout.write(f"Pedidos con mockups purgados: {stats['purged_orders']}")
            return

        if options['all']:
            self.stdout.write("Purgando todos los archivos de mockup existentes...")
            result = purge_all_mockup_files()
            self.stdout.write(self.style.SUCCESS(
                f"[OK] {result['deleted_files']} archivos eliminados del disco. "
                f"Espacio liberado: {result['freed_mb']} MB. "
                f"{result['updated_orders']} pedidos actualizados en base de datos."
            ))
            return

        # Limpieza inteligente (visualizados + expirados + huérfanos)
        self.stdout.write("Ejecutando limpieza inteligente de mockups...")
        result = auto_cleanup_viewed_and_expired_mockups(
            max_viewed_age_minutes=0 if options['viewed'] else 30,
            max_unviewed_age_hours=options['hours'],
            purge_immediate_viewed=options['viewed']
        )
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Limpieza completada. Pedidos limpiados: {result['orders_cleaned']}, "
            f"Archivos huerfanos eliminados: {result['orphan_files_deleted']}"
        ))
