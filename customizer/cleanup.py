import os
import glob
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_mockups_dir():
    """Retorna la ruta absoluta del directorio donde se almacenan los mockups."""
    return os.path.join(settings.MEDIA_ROOT, 'orders', 'mockups')


def get_mockups_storage_stats():
    """
    Retorna métricas de almacenamiento de los mockups en disco.
    """
    mockups_dir = get_mockups_dir()
    total_files = 0
    total_bytes = 0

    if os.path.exists(mockups_dir):
        for root, _, files in os.walk(mockups_dir):
            for f in files:
                filepath = os.path.join(root, f)
                if os.path.isfile(filepath):
                    total_files += 1
                    try:
                        total_bytes += os.path.getsize(filepath)
                    except OSError:
                        pass

    from customizer.models import Order
    total_orders = Order.objects.count()
    purged_orders = Order.objects.filter(mockups_purged=True).count()
    viewed_orders = Order.objects.filter(is_viewed=True).count()

    return {
        'total_files': total_files,
        'total_bytes': total_bytes,
        'total_mb': round(total_bytes / (1024 * 1024), 2),
        'total_orders': total_orders,
        'purged_orders': purged_orders,
        'viewed_orders': viewed_orders,
    }


def purge_empty_dirs(base_dir=None):
    """Elimina carpetas vacías dentro del árbol de mockups."""
    if base_dir is None:
        base_dir = get_mockups_dir()
    if not os.path.exists(base_dir):
        return 0

    deleted_dirs = 0
    for root, dirs, _ in os.walk(base_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    deleted_dirs += 1
            except OSError:
                pass
    return deleted_dirs


def purge_all_mockup_files():
    """
    Elimina TODOS los archivos de mockups existentes hasta el momento en el servidor.
    Actualiza los pedidos en la base de datos marcando mockups_purged=True.
    Libera espacio total de almacenamiento.
    """
    mockups_dir = get_mockups_dir()
    deleted_files = 0
    freed_bytes = 0

    if os.path.exists(mockups_dir):
        for root, _, files in os.walk(mockups_dir):
            for f in files:
                filepath = os.path.join(root, f)
                try:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_files += 1
                    freed_bytes += size
                except OSError as e:
                    logger.warning(f"No se pudo eliminar {filepath}: {e}")

    # Limpiar directorios vacíos
    purge_empty_dirs(mockups_dir)

    # Actualizar pedidos en la base de datos
    from customizer.models import Order
    updated_orders = Order.objects.filter(mockups_purged=False).update(mockups_purged=True)

    return {
        'deleted_files': deleted_files,
        'freed_bytes': freed_bytes,
        'freed_mb': round(freed_bytes / (1024 * 1024), 2),
        'updated_orders': updated_orders,
    }


def purge_order_mockup_files(order):
    """
    Elimina físicamente los archivos PNG de mockup de un pedido específico.
    """
    return order.purge_mockup_files()


def auto_cleanup_viewed_and_expired_mockups(
    max_viewed_age_minutes=30,
    max_unviewed_age_hours=24,
    purge_immediate_viewed=False
):
    """
    Limpieza inteligente del sistema:
    1. Elimina mockups de pedidos que ya fueron visualizados desde WhatsApp/Enlace
       (después de una ventana de gracia opcional, o inmediatamente si purge_immediate_viewed=True).
    2. Elimina mockups antiguos sin visualizar que superen max_unviewed_age_hours.
    3. Elimina archivos huérfanos que ya no pertenezcan a ningún pedido activo.
    """
    from customizer.models import Order
    now = timezone.now()
    deleted_files = 0
    orders_cleaned = 0

    # 1. Pedidos visualizados
    if purge_immediate_viewed:
        viewed_orders = Order.objects.filter(is_viewed=True, mockups_purged=False)
    else:
        threshold_viewed = now - timedelta(minutes=max_viewed_age_minutes)
        viewed_orders = Order.objects.filter(
            is_viewed=True,
            mockups_purged=False,
            viewed_at__lte=threshold_viewed
        )

    for order in viewed_orders:
        if order.purge_mockup_files():
            orders_cleaned += 1

    # 2. Pedidos no visualizados pero expirados (más de X horas)
    threshold_unviewed = now - timedelta(hours=max_unviewed_age_hours)
    expired_orders = Order.objects.filter(
        mockups_purged=False,
        created_at__lte=threshold_unviewed
    )
    for order in expired_orders:
        if order.purge_mockup_files():
            orders_cleaned += 1

    # 3. Eliminar archivos huérfanos en media/orders/mockups/
    mockups_dir = get_mockups_dir()
    active_paths = set()
    for o in Order.objects.filter(mockups_purged=False):
        if o.front_design_image:
            try:
                active_paths.add(os.path.normpath(o.front_design_image.path))
            except Exception:
                pass
        if o.back_design_image:
            try:
                active_paths.add(os.path.normpath(o.back_design_image.path))
            except Exception:
                pass

    if os.path.exists(mockups_dir):
        for root, _, files in os.walk(mockups_dir):
            for f in files:
                filepath = os.path.normpath(os.path.join(root, f))
                if filepath not in active_paths:
                    try:
                        os.remove(filepath)
                        deleted_files += 1
                    except OSError:
                        pass

    purge_empty_dirs(mockups_dir)

    return {
        'orders_cleaned': orders_cleaned,
        'orphan_files_deleted': deleted_files,
    }
