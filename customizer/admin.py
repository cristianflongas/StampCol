from django.contrib import admin
from django.utils.html import format_html
from .models import ProductOption, DesignAsset, Order

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'option_type', 'color_preview', 'extra_price', 'is_active', 'display_order')
    list_filter = ('option_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('display_order', 'name')

    def color_preview(self, obj):
        if obj.code_hex:
            return format_html(
                '<div style="width: 28px; height: 28px; background-color: {}; border-radius: 6px; border: 1px solid #ccc; display: inline-block;"></div> <span style="vertical-align: middle; margin-left: 6px;">{}</span>',
                obj.code_hex, obj.code_hex
            )
        return '-'
    color_preview.short_description = 'Muestra de Color'


@admin.register(DesignAsset)
class DesignAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'thumbnail', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px; background: #eee; padding: 2px;" />', obj.image.url)
        return '-'
    thumbnail.short_description = 'Previsualización'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone_number', 'garment_type', 'size', 'color', 'fabric_type', 'status', 'created_at', 'whatsapp_action', 'pinterest_link_action', 'mockup_previews')
    list_filter = ('garment_type', 'status', 'size', 'color', 'created_at')
    search_fields = ('customer_name', 'phone_number', 'ai_instructions', 'additional_notes', 'pinterest_url')
    readonly_fields = ('created_at', 'front_mockup_preview', 'back_mockup_preview', 'pinterest_link_detail')

    def pinterest_link_action(self, obj):
        if obj.pinterest_url:
            urls = [u.strip() for u in obj.pinterest_url.split() if u.strip().startswith('http')]
            if urls:
                return format_html(
                    '<a href="{}" target="_blank" style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px; background: #e60023; color: #fff; font-size: 11px; font-weight: bold; text-decoration: none;">📌 Pinterest</a>',
                    urls[0]
                )
            return obj.pinterest_url[:30] + '...'
        return '-'
    pinterest_link_action.short_description = 'Pinterest'

    def pinterest_link_detail(self, obj):
        if obj.pinterest_url:
            lines = obj.pinterest_url.splitlines()
            links_html = []
            for line in lines:
                line_str = line.strip()
                if line_str.startswith('http'):
                    links_html.append(f'<a href="{line_str}" target="_blank" style="color: #e60023; font-weight: bold; text-decoration: underline;">{line_str}</a>')
                elif line_str:
                    links_html.append(line_str)
            return format_html('<br>'.join(links_html))
        return 'No se especificó link de Pinterest'
    pinterest_link_detail.short_description = 'Links de Pinterest / Referencias'

    def whatsapp_action(self, obj):
        if obj.phone_number:
            clean_phone = ''.join(c for c in obj.phone_number if c.isdigit())
            if not clean_phone.startswith('57') and len(clean_phone) == 10:
                clean_phone = '57' + clean_phone
            return format_html(
                '<a href="https://wa.me/{}" target="_blank" style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px; background: #059669; color: #fff; font-size: 11px; font-weight: bold; text-decoration: none;">💬 WhatsApp</a>',
                clean_phone
            )
        return '-'
    whatsapp_action.short_description = 'Contactar'

    def mockup_previews(self, obj):
        html = ''
        if obj.front_design_image:
            html += format_html('<a href="{}" target="_blank" title="Frente"><img src="{}" style="max-height: 38px; border-radius: 4px; margin-right: 5px; border: 1px solid #ddd; background: #fafafa;"/></a>', obj.front_design_image.url, obj.front_design_image.url)
        if obj.back_design_image:
            html += format_html('<a href="{}" target="_blank" title="Espalda"><img src="{}" style="max-height: 38px; border-radius: 4px; border: 1px solid #ddd; background: #fafafa;"/></a>', obj.back_design_image.url, obj.back_design_image.url)
        return format_html(html) if html else '-'
    mockup_previews.short_description = 'Mockups'

    def front_mockup_preview(self, obj):
        if obj.front_design_image:
            return format_html('<img src="{}" style="max-width: 320px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/>', obj.front_design_image.url)
        return 'No disponible'
    front_mockup_preview.short_description = 'Diseño Frontal'

    def back_mockup_preview(self, obj):
        if obj.back_design_image:
            return format_html('<img src="{}" style="max-width: 320px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/>', obj.back_design_image.url)
        return 'No disponible'
    back_mockup_preview.short_description = 'Diseño Trasero'

