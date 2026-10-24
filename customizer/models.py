from django.db import models

class ProductOption(models.Model):
    """
    Modelo para opciones de personalización de camisetas:
    - Colores disponibles (con código HEX y/o imagen base)
    - Tallas (S, M, L, XL, Oversize)
    - Tipos de tela (100% Algodón Peinado, Algodón Pesado Streetwear)
    """
    OPTION_TYPE_CHOICES = [
        ('COLOR', 'Color de Camiseta'),
        ('SIZE', 'Talla'),
        ('FABRIC', 'Tipo de Tela'),
    ]

    option_type = models.CharField(
        'Tipo de Opción',
        max_length=20,
        choices=OPTION_TYPE_CHOICES,
        db_index=True
    )
    name = models.CharField('Nombre / Etiqueta', max_length=100)
    code_hex = models.CharField(
        'Código HEX (Colores)',
        max_length=10,
        blank=True,
        null=True,
        help_text='Ej: #1A1A1A, #F5F5F5, #2563EB'
    )
    base_image = models.ImageField(
        'Imagen Base o Textura',
        upload_to='product_options/',
        blank=True,
        null=True,
        help_text='Opcional: Si se desea una imagen pre-renderizada del buzo en este color'
    )
    description = models.CharField(
        'Descripción o Característica',
        max_length=255,
        blank=True,
        help_text='Ej: 280g suave al tacto, corte unisex, etc.'
    )
    extra_price = models.DecimalField(
        'Precio adicional (COP)',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    is_active = models.BooleanField('Activo', default=True)
    display_order = models.PositiveIntegerField('Orden de aparición', default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Opción de Producto'
        verbose_name_plural = 'Opciones de Producto'

    def __str__(self):
        return f"[{self.get_option_type_display()}] {self.name}"


class DesignAsset(models.Model):
    """
    Modelo para almacenar gráficos, stickers y estampados prediseñados
    organizados por categorías temáticas.
    """
    CATEGORY_CHOICES = [
        ('URBANO', 'Streetwear & Urbano'),
        ('ANIME', 'Anime & Manga'),
        ('MINIMAL', 'Minimalista'),
        ('FRASES', 'Frases & Tipografía'),
        ('RETRO', 'Vintage & Retro'),
        ('GAMING', 'Gaming & Geek'),
        ('BOTANICO', 'Naturaleza & Floral'),
    ]

    title = models.CharField('Título o Nombre del Diseño', max_length=120)
    category = models.CharField(
        'Categoría',
        max_length=40,
        choices=CATEGORY_CHOICES,
        default='URBANO',
        db_index=True
    )
    image = models.ImageField(
        'Archivo de Estampado (PNG / SVG)',
        upload_to='design_assets/'
    )
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)

    class Meta:
        ordering = ['category', 'title']
        verbose_name = 'Estampado Prediseñado'
        verbose_name_plural = 'Estampados Prediseñados'

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class Order(models.Model):
    """
    Modelo para registrar y auditar los pedidos de buzos personalizados:
    Datos del cliente, especificaciones del buzo, imágenes renderizadas del Canvas
    (frente y espalda) y recomendaciones/prompts de la IA.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente (Redirigido a WhatsApp)'),
        ('CONFIRMED', 'Confirmado por Asesor'),
        ('IN_PRODUCTION', 'En Estampado / Producción'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]

    customer_name = models.CharField('Nombre del Cliente', max_length=150)
    phone_number = models.CharField('Teléfono / WhatsApp', max_length=30)
    garment_type = models.CharField('Tipo de Prenda', max_length=60, default='Camiseta Cuello Redondo')
    size = models.CharField('Talla', max_length=20)
    color = models.CharField('Color de la Camiseta', max_length=60)
    fabric_type = models.CharField('Tipo de Tela', max_length=120)
    
    # Archivos generados desde el Canvas HTML5 (Base64 -> ImageField)
    front_design_image = models.ImageField(
        'Mockup Frontal Generado',
        upload_to='orders/mockups/front/%Y/%m/',
        blank=True,
        null=True
    )
    back_design_image = models.ImageField(
        'Mockup Trasero Generado',
        upload_to='orders/mockups/back/%Y/%m/',
        blank=True,
        null=True
    )
    design_document = models.ImageField(
        'Documento Oficial de Creación / Hoja de Confección',
        upload_to='orders/documents/%Y/%m/',
        blank=True,
        null=True
    )

    ai_instructions = models.TextField(
        'Instrucciones / Sugerencias de la IA Gemini',
        blank=True,
        default=''
    )
    additional_notes = models.TextField(
        'Notas adicionales del cliente',
        blank=True,
        default=''
    )

    pinterest_url = models.TextField(
        'URL(s) de Pinterest / Referencia de Estampado',
        blank=True,
        default=''
    )

    status = models.CharField(
        'Estado del Pedido',
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    is_viewed = models.BooleanField(
        'Visualizado desde WhatsApp/Enlace',
        default=False,
        db_index=True
    )
    viewed_at = models.DateTimeField(
        'Fecha de Primera Visualización',
        null=True,
        blank=True
    )
    mockups_purged = models.BooleanField(
        'Mockups Purgados del Disco',
        default=False,
        db_index=True
    )
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido Personalizado'
        verbose_name_plural = 'Pedidos Personalizados'

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer_name} ({self.size}, {self.color})"

    def purge_mockup_files(self):
        """
        Elimina físicamente del disco los archivos PNG de mockup generados
        para este pedido para evitar acumulación de archivos en el servidor.
        """
        import os
        purged_any = False
        for field in [self.front_design_image, self.back_design_image, self.design_document]:
            if field and hasattr(field, 'path'):
                try:
                    if os.path.isfile(field.path):
                        os.remove(field.path)
                        purged_any = True
                except Exception:
                    pass
        self.mockups_purged = True
        self.save(update_fields=['mockups_purged'])
        return purged_any
