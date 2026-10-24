import json
import urllib.parse
from django.test import TestCase, Client
from django.urls import reverse
from customizer.models import ProductOption, Order

class CustomizerViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.color = ProductOption.objects.create(
            option_type='COLOR',
            name='Negro Test',
            code_hex='#111111',
            is_active=True
        )

    def test_index_view(self):
        response = self.client.get(reverse('customizer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'StampCol')
        self.assertContains(response, 'Negro Test')

    def test_index_no_ai_chat_and_has_garment_selectors(self):
        response = self.client.get(reverse('customizer:index'))
        self.assertEqual(response.status_code, 200)
        # Verificar que el chat con IA fue removido por completo
        self.assertNotContains(response, 'id="gemini-chat-form"')
        self.assertNotContains(response, 'id="gemini-user-prompt"')
        self.assertNotContains(response, 'id="design-subtab-ai"')
        self.assertNotContains(response, 'gemini_chat.js')
        
        # Verificar que el visor está unificado y existen los selectores de confección
        self.assertContains(response, 'Camiseta • Frente')
        self.assertContains(response, 'id="btn-prenda-camiseta"')
        self.assertContains(response, 'id="btn-prenda-oversize"')
        self.assertNotContains(response, 'id="btn-prenda-buzo"')
        self.assertNotContains(response, 'Buzo Hoodie')
        self.assertContains(response, 'id="fabric-options-container"')
        self.assertContains(response, 'id="id_garment_type"')

    def test_gemini_assistant_view(self):
        response = self.client.post(
            reverse('customizer:gemini_assistant'),
            data=json.dumps({
                'prompt': 'Quiero una camiseta estilo anime cyberpunk',
                'color': 'Negro Test',
                'fabric': '100% Algodón Peinado'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('response', data)
        self.assertIsNotNone(data.get('isolated_stamp'))
        self.assertIn('suggested_meta', data)
        self.assertIn('suggested_options', data)
        self.assertEqual(data['suggested_options'][0]['label'], 'Añadir más detalles')
        self.assertEqual(data['suggested_options'][1]['label'], 'Cambiar estilo')

    def test_gemini_assistant_dragon_prompt(self):
        response = self.client.post(
            reverse('customizer:gemini_assistant'),
            data=json.dumps({
                'prompt': 'Dragón Minimal',
                'color': 'Blanco'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('isolated_stamp'), '/static/customizer/images/samples/dragon_minimal.png')
        self.assertEqual(data.get('suggested_meta', {}).get('suggested_placement'), 'front')

    def test_gemini_assistant_tree_prompt(self):
        response = self.client.post(
            reverse('customizer:gemini_assistant'),
            data=json.dumps({
                'prompt': 'quieroun arbol de',
                'color': 'Naranja'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(data.get('isolated_stamp', '').startswith('data:image/'))
        # Verificar que el estampado no imprime el mensaje del usuario como texto en un banner
        raw_b64 = data.get('isolated_stamp')
        self.assertNotIn('QUIEROUN ARBOL DE', raw_b64)


    def test_save_order_view(self):
        response = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps({
                'customer_name': 'Juan Pérez',
                'phone_number': '3171535408',
                'garment_type': 'Camiseta Cuello Redondo Clásica',
                'size': 'L',
                'color': 'Negro Test',
                'fabric_type': '100% Algodón Peinado 180g',
                'additional_notes': 'Prueba de pedido',
                'front_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
                'back_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('whatsapp_url', data)
        order = Order.objects.get(customer_name='Juan Pérez')
        self.assertEqual(order.garment_type, 'Camiseta Cuello Redondo Clásica')

    def test_save_order_camiseta_oversize(self):
        response = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps({
                'customer_name': 'Camila Gómez',
                'phone_number': '3129876543',
                'garment_type': 'Camiseta Oversize Streetwear',
                'size': 'XL',
                'color': 'Negro Test',
                'fabric_type': 'Algodón Pesado Streetwear 220g',
                'additional_notes': 'Diseño en espalda grande',
                'front_design_base64': '',
                'back_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('whatsapp_url', data)
        # Verificar que el mensaje de WhatsApp contiene la información de Camiseta y Tela
        self.assertIn('Camiseta', data['whatsapp_url'])
        self.assertIn('Streetwear', data['whatsapp_url'])
        order = Order.objects.get(customer_name='Camila Gómez')
        self.assertEqual(order.garment_type, 'Camiseta Oversize Streetwear')
        self.assertEqual(order.fabric_type, 'Algodón Pesado Streetwear 220g')

    def test_isolate_stamp_view(self):
        # Enviar un PNG válido de prueba
        valid_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAFklEQVR4nGP8//8/A27AhEeOYeRKAwCl4wMRx3ocVQAAAABJRU5ErkJggg=='
        response = self.client.post(
            reverse('customizer:isolate_stamp'),
            data=json.dumps({
                'image_base64': valid_b64
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('isolated_image', data)
        self.assertIn('isolated_stamp_base64', data)

    def test_analyze_stamp_vision_view(self):
        valid_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAFklEQVR4nGP8//8/A27AhEeOYeRKAwCl4wMRx3ocVQAAAABJRU5ErkJggg=='
        response = self.client.post(
            reverse('customizer:analyze_stamp_vision'),
            data=json.dumps({
                'image_base64': valid_b64
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(data.get('is_suitable'))
        self.assertIn('verdict', data)
        self.assertIn('analysis', data)
        self.assertIn('isolated_image', data)
        self.assertIn('suggested_meta', data)

    def test_gemini_assistant_edit_uploaded_image(self):
        valid_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAFklEQVR4nGP8//8/A27AhEeOYeRKAwCl4wMRx3ocVQAAAABJRU5ErkJggg=='
        response = self.client.post(
            reverse('customizer:gemini_assistant'),
            data=json.dumps({
                'prompt': 'Quítale el fondo blanco para dejarlo transparente',
                'image_base64': valid_b64,
                'color': 'Blanco'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('response', data)
        self.assertIn('isolated_stamp', data)
        self.assertEqual(data['suggested_meta']['suggested_color_name'], 'Negro')

    def test_isolate_stamp_with_geometric_shapes(self):
        valid_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAFklEQVR4nGP8//8/A27AhEeOYeRKAwCl4wMRx3ocVQAAAABJRU5ErkJggg=='
        all_shapes = ['circle', 'triangle', 'rounded_rect', 'hexagon', 'heart', 'star', 'diamond', 'original']
        for shape in all_shapes:
            response = self.client.post(
                reverse('customizer:isolate_stamp'),
                data=json.dumps({
                    'image_base64': valid_b64,
                    'shape': shape
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get('status'), 'success')
            self.assertIn('isolated_image', data)
            self.assertTrue(data['isolated_image'].startswith('data:image/png;base64,'))

    def test_isolate_stamp_static_sample_shapes(self):
        # Verificar que una imagen de muestra estática como neko_spidercat.png se puede recortar a círculo y triángulo
        sample_path = '/static/customizer/images/samples/neko_spidercat.png'
        for shape in ['circle', 'triangle', 'heart', 'star', 'original']:
            response = self.client.post(
                reverse('customizer:isolate_stamp'),
                data=json.dumps({
                    'image_base64': sample_path,
                    'shape': shape
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get('status'), 'success')
            self.assertIn('isolated_image', data)
            self.assertTrue(data['isolated_image'].startswith('data:image/png;base64,'))

    def test_gemini_assistant_shape_prompt(self):
        valid_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAFklEQVR4nGP8//8/A27AhEeOYeRKAwCl4wMRx3ocVQAAAABJRU5ErkJggg=='
        response = self.client.post(
            reverse('customizer:gemini_assistant'),
            data=json.dumps({
                'prompt': 'Haz mi imagen redonda en un círculo perfecto',
                'image_base64': valid_b64,
                'color': 'Blanco'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('isolated_stamp', data)
        self.assertIn('Circular', data.get('response', ''))

    def test_fetch_external_image_validation(self):
        # Validación de URL inválida
        response = self.client.post(
            reverse('customizer:fetch_external_image'),
            data=json.dumps({'url': 'not_a_valid_url'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_extract_pin_image_url_helper(self):
        from customizer.views import extract_pin_image_url
        # URL no existente o inválida retorna None de forma segura
        res = extract_pin_image_url('https://invalid-non-existent-domain-12345.com/pin/123')
        self.assertIsNone(res)

    def test_index_contains_manual_eraser_and_bg_toggle(self):
        response = self.client.get(reverse('customizer:index'))
        self.assertEqual(response.status_code, 200)
        # Verificar botones de fondo y borrador manual
        self.assertContains(response, 'id="btn-toggle-bg-action"')
        self.assertContains(response, 'id="btn-open-manual-eraser"')
        self.assertContains(response, 'id="manual-eraser-modal"')
        self.assertContains(response, 'id="eraser-canvas"')
        self.assertContains(response, 'Borrador Manual & Retoque de Fondo')
        self.assertContains(response, 'id="eraser-mode-erase"')
        self.assertContains(response, 'id="eraser-mode-restore"')

    def test_save_order_records_client_data_and_garment(self):
        # Probar que el pedido guarda todos los datos del cliente y genera enlace de WhatsApp
        client_data = {
            'customer_name': 'Carlos Rodríguez',
            'phone_number': '3157894561',
            'garment_type': 'Camiseta Oversize Streetwear',
            'size': 'Oversize',
            'color': 'Negro Streetwear',
            'fabric_type': 'Algodón Pesado Streetwear 220g',
            'additional_notes': 'Entregar en Campoalegre en horas de la tarde',
            'front_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'back_design_base64': ''
        }
        response = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps(client_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('whatsapp_url', data)

        # Verificar en base de datos
        order = Order.objects.get(phone_number='3157894561')
        self.assertEqual(order.customer_name, 'Carlos Rodríguez')
        self.assertEqual(order.garment_type, 'Camiseta Oversize Streetwear')
        self.assertEqual(order.size, 'Oversize')
        self.assertEqual(order.color, 'Negro Streetwear')
        self.assertEqual(order.fabric_type, 'Algodón Pesado Streetwear 220g')
        self.assertEqual(order.status, 'PENDING')
        self.assertTrue(bool(order.front_design_image))

    def test_order_admin_renders_correctly(self):
        from django.contrib.admin.sites import AdminSite
        from customizer.admin import OrderAdmin
        order = Order.objects.create(
            customer_name='Admin Test User',
            phone_number='3112223344',
            garment_type='Camiseta Cuello Redondo',
            size='L',
            color='Blanco Puro',
            fabric_type='100% Algodón Peinado 180g'
        )
        admin_site = AdminSite()
        order_admin = OrderAdmin(Order, admin_site)
        wa_link = order_admin.whatsapp_action(order)
        self.assertIn('https://wa.me/573112223344', wa_link)
        self.assertIn('garment_type', order_admin.list_display)
        self.assertIn('garment_type', order_admin.list_filter)

    def test_save_order_with_pinterest_and_mockups(self):
        client_data = {
            'customer_name': 'Cristian Longas',
            'phone_number': '3023012409',
            'garment_type': 'Camiseta Cuello Redondo',
            'size': 'M',
            'color': 'Negro Streetwear (#121212)',
            'fabric_type': '100% Algodón Peinado 180g',
            'additional_notes': 'campoalegre',
            'pinterest_url': 'https://es.pinterest.com/pin/987654321/',
            'front_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'back_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        }
        response = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps(client_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('whatsapp_url', data)
        self.assertIn('front_mockup_url', data)
        self.assertIn('order_preview_url', data)

        # Verificar que el mensaje codificado de WhatsApp contiene los datos comerciales limpios sin enlaces internos
        decoded_wa = urllib.parse.unquote(data['whatsapp_url'])
        self.assertIn('SOLICITUD DE COTIZACIÓN', decoded_wa)
        self.assertIn('Cristian Longas', decoded_wa)
        self.assertIn('https://es.pinterest.com/pin/987654321/', decoded_wa)
        self.assertIn('Te adjunto la imagen de mi diseño', decoded_wa)
        self.assertNotIn('Mockup Frente:', decoded_wa)
        self.assertNotIn('Ver Ficha Técnica Online', decoded_wa)

        # Verificar en base de datos
        order = Order.objects.get(id=data['order_id'])
        self.assertEqual(order.pinterest_url, 'https://es.pinterest.com/pin/987654321/')
        self.assertTrue(bool(order.front_design_image))
        self.assertTrue(bool(order.back_design_image))

    def test_order_preview_view(self):
        order = Order.objects.create(
            customer_name='Valentina Morales',
            phone_number='3145678901',
            garment_type='Camiseta Oversize Streetwear',
            size='S',
            color='Blanco',
            fabric_type='100% Algodón Peinado 180g',
            pinterest_url='https://pin.it/example123'
        )
        response = self.client.get(reverse('customizer:order_preview', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valentina Morales')
        self.assertContains(response, 'Camiseta Oversize Streetwear')
        self.assertContains(response, 'https://pin.it/example123')
        self.assertContains(response, 'Ficha Técnica de Producción')


class ResponsiveAndUserFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1'
        }

    def test_mobile_responsive_html_structure(self):
        """Verifica que el HTML incluye todas las meta etiquetas, clases y controles para 100% responsive."""
        response = self.client.get(reverse('customizer:index'), **self.mobile_headers)
        self.assertEqual(response.status_code, 200)
        
        # 1. Viewport con viewport-fit=cover para soporte de notch y dynamic island
        self.assertContains(response, 'viewport-fit=cover')
        
        # 2. Barra inferior móvil fija con safe-bottom y switcher rápido
        self.assertContains(response, 'id="mobile-toggle-view-btn"')
        self.assertContains(response, 'id="mobile-toggle-view-text"')
        self.assertContains(response, 'id="btn-open-mobile-checkout-modal"')
        self.assertContains(response, 'safe-bottom')
        
        # 3. Modal móvil con campos requeridos y opcional de Pinterest
        self.assertContains(response, 'id="mobile-checkout-modal"')
        self.assertContains(response, 'id="mobile-customer-name"')
        self.assertContains(response, 'id="mobile-customer-phone"')
        self.assertContains(response, 'id="mobile-customer-notes"')
        self.assertContains(response, 'id="mobile-pinterest-url"')
        self.assertContains(response, 'id="btn-submit-order-mobile"')
        
        # 4. Botones de acción del lienzo responsivos (Borrador, Quitar Fondo, Centrar, Figuras)
        self.assertContains(response, 'id="btn-toggle-bg-action"')
        self.assertContains(response, 'id="btn-open-manual-eraser"')
        self.assertContains(response, 'id="btn-center-design"')
        self.assertContains(response, 'id="btn-duplicate-design"')
        self.assertContains(response, 'id="btn-remove-design"')
        self.assertContains(response, 'id="hoodie-shape-buttons"')

    def test_mobile_user_simulation_complete_flow(self):
        """
        Simula el viaje completo de un usuario en un smartphone:
        1. Carga la página desde un móvil.
        2. Procesa recorte y aislamiento de estampado con IA.
        3. Envía su cotización personalizada con link de Pinterest.
        4. Accede a la ficha técnica de producción generada.
        """
        # 1. Carga inicial
        res_page = self.client.get(reverse('customizer:index'), **self.mobile_headers)
        self.assertEqual(res_page.status_code, 200)

        # 2. Simulación de procesamiento de estampado (quitar fondo / aislar)
        fake_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        res_isolate = self.client.post(
            reverse('customizer:isolate_stamp'),
            data=json.dumps({
                'image_base64': fake_b64,
                'shape': 'circle',
                'remove_bg': True
            }),
            content_type='application/json',
            **self.mobile_headers
        )
        self.assertEqual(res_isolate.status_code, 200)
        isolate_data = res_isolate.json()
        self.assertEqual(isolate_data.get('status'), 'success')
        self.assertTrue(bool(isolate_data.get('isolated_image')))

        # 3. Envío de cotización móvil por WhatsApp
        order_payload = {
            'customer_name': 'Camila Andrade',
            'phone_number': '3187654321',
            'garment_type': 'Camiseta Oversize Streetwear',
            'size': 'L',
            'color': 'Negro Streetwear (#121212)',
            'fabric_type': 'Algodón Pesado Streetwear 220g',
            'additional_notes': 'Envío a Campoalegre centro',
            'pinterest_url': 'https://co.pinterest.com/pin/1122334455/',
            'front_design_base64': fake_b64,
            'back_design_base64': fake_b64
        }
        res_order = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps(order_payload),
            content_type='application/json',
            **self.mobile_headers
        )
        self.assertEqual(res_order.status_code, 200)
        order_res_data = res_order.json()
        self.assertEqual(order_res_data.get('status'), 'success')
        self.assertIn('whatsapp_url', order_res_data)
        self.assertIn('order_preview_url', order_res_data)

        # 4. Validar contenido del link a WhatsApp
        decoded_wa = urllib.parse.unquote(order_res_data['whatsapp_url'])
        self.assertIn('Camila Andrade', decoded_wa)
        self.assertIn('3187654321', decoded_wa)
        self.assertIn('Camiseta Oversize Streetwear', decoded_wa)
        self.assertIn('https://co.pinterest.com/pin/1122334455/', decoded_wa)
        self.assertIn('Campoalegre centro', decoded_wa)

        # 5. Carga de la Ficha Técnica para el negocio/cliente
        order_id = order_res_data['order_id']
        res_preview = self.client.get(
            reverse('customizer:order_preview', args=[order_id]),
            **self.mobile_headers
        )
        self.assertEqual(res_preview.status_code, 200)
        self.assertContains(res_preview, 'Camila Andrade')
        self.assertContains(res_preview, '3187654321')
        self.assertContains(res_preview, 'https://co.pinterest.com/pin/1122334455/')

    def test_responsive_meta_and_layout_structure(self):
        """
        Verifica que el sistema esté completamente configurado para dispositivos móviles:
        - Meta viewport en templates principales.
        - Clases responsivas de Tailwind CSS.
        - Hero con animación de logo y 2 columnas adaptables.
        """
        # 1. Página principal
        res = self.client.get(reverse('customizer:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'name="viewport"')
        self.assertContains(res, 'width=device-width')
        self.assertContains(res, 'float-logo-animation')
        self.assertContains(res, 'pulse-aura-animation')
        self.assertContains(res, 'grid-cols-1')
        self.assertContains(res, 'safe-bottom')

        # 2. Ficha técnica (order_preview)
        order = Order.objects.create(
            customer_name='Prueba Responsive',
            phone_number='3001234567',
            garment_type='Camiseta Cuello Redondo',
            size='M',
            color='Blanco',
            fabric_type='100% Algodón Peinado'
        )
        res_order = self.client.get(reverse('customizer:order_preview', args=[order.id]))
        self.assertEqual(res_order.status_code, 200)
        self.assertContains(res_order, 'name="viewport"')
        self.assertContains(res_order, 'width=device-width')

    def test_order_preview_marks_viewed_timestamp(self):
        """
        Verifica que cuando un cliente o taller abre el enlace de WhatsApp (order_preview),
        el pedido se marque automáticamente como visualizado y registre la fecha.
        """
        order = Order.objects.create(
            customer_name='Test Visualización',
            phone_number='3110001122',
            garment_type='Camiseta Oversize',
            size='XL',
            color='Negro',
            fabric_type='Algodón Pesado 220g'
        )
        self.assertFalse(order.is_viewed)
        self.assertIsNone(order.viewed_at)

        response = self.client.get(reverse('customizer:order_preview', args=[order.id]))
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.assertTrue(order.is_viewed)
        self.assertIsNotNone(order.viewed_at)

    def test_purge_order_mockup_endpoint_and_file_removal(self):
        """
        Verifica que el endpoint de purga elimine físicamente los archivos del disco
        y actualice el estado mockups_purged a True.
        """
        import os
        from django.core.files.base import ContentFile

        order = Order.objects.create(
            customer_name='Cliente Purga',
            phone_number='3159998877',
            garment_type='Camiseta Cuello Redondo',
            size='S',
            color='Negro',
            fabric_type='100% Algodón Peinado'
        )
        # Guardar un archivo dummy en el campo
        dummy_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        order.front_design_image.save('test_mockup_front.png', ContentFile(dummy_content), save=True)
        file_path = order.front_design_image.path
        self.assertTrue(os.path.isfile(file_path))

        # Llamar al endpoint de purga
        response = self.client.post(reverse('customizer:purge_order_mockup', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(data.get('purged'))

        order.refresh_from_db()
        self.assertTrue(order.mockups_purged)
        # Verificar que el archivo fue eliminado físicamente del disco
        self.assertFalse(os.path.isfile(file_path))

    def test_order_preview_graceful_rendering_when_purged(self):
        """
        Verifica que al consultar la ficha técnica de un pedido cuyos mockups
        fueron purgados del servidor, se muestre el aviso informativo sin error 500.
        """
        order = Order.objects.create(
            customer_name='Cliente Pedido Purgado',
            phone_number='3161234567',
            garment_type='Camiseta Oversize Streetwear',
            size='M',
            color='Blanco',
            fabric_type='Algodón Pesado 220g',
            mockups_purged=True
        )
        response = self.client.get(reverse('customizer:order_preview', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mockup visualizado y purgado del servidor')
        self.assertContains(response, 'Cliente Pedido Purgado')

    def test_management_command_cleanup_mockups(self):
        """
        Verifica que el comando management `cleanup_mockups` funcione correctamente
        con los flags --stats, --all y --viewed.
        """
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        # 1. Probar flag --stats
        call_command('cleanup_mockups', stats=True, stdout=out)
        self.assertIn('Estado del Almacenamiento', out.getvalue())

        # 2. Probar flag --all
        out_all = StringIO()
        call_command('cleanup_mockups', all=True, stdout=out_all)
        self.assertIn('archivos eliminados', out_all.getvalue())

        # 3. Probar flag --viewed
        out_viewed = StringIO()
        call_command('cleanup_mockups', viewed=True, stdout=out_viewed)
        self.assertIn('Limpieza completada', out_viewed.getvalue())

    def test_whatsapp_text_clean_and_no_localhost_links(self):
        """
        Verifica que el texto generado para WhatsApp no contenga enlaces de localhost,
        127.0.0.1 ni links técnicos, sino únicamente los datos del pedido y el mensaje
        limpio para adjuntar la foto directamente.
        """
        response = self.client.post(
            reverse('customizer:save_order'),
            data=json.dumps({
                'customer_name': 'Carlos Rodríguez',
                'phone_number': '3171535408',
                'garment_type': 'Camiseta Oversize Streetwear',
                'size': 'L',
                'color': 'Blanco',
                'fabric_type': 'Algodón Pesado Streetwear 220g',
                'additional_notes': 'Sin notas',
                'front_design_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('wa_text', data)
        wa_text = data['wa_text']
        self.assertNotIn('localhost', wa_text.lower())
        self.assertNotIn('127.0.0.1', wa_text)
        self.assertNotIn('http://', wa_text.lower())
        self.assertIn('Carlos Rodríguez', wa_text)
        self.assertIn('Camiseta Oversize Streetwear', wa_text)
        self.assertIn('Algodón Pesado Streetwear 220g', wa_text)
        self.assertIn('Te adjunto la imagen de mi diseño', wa_text)

    def test_fetch_external_image_validation(self):
        """
        Verifica la validación del endpoint /api/fetch-external-image/ ante URLs vacías o inválidas.
        """
        # 1. URL vacía
        resp = self.client.post(
            reverse('customizer:fetch_external_image'),
            data=json.dumps({'url': ''}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

        # 2. URL no http/https
        resp = self.client.post(
            reverse('customizer:fetch_external_image'),
            data=json.dumps({'url': 'ftp://example.com/image.png'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_render_production_settings_configured(self):
        """
        Verifica que la configuración del proyecto incluya los parámetros requeridos para Render:
        - .onrender.com en ALLOWED_HOSTS
        - https://*.onrender.com en CSRF_TRUSTED_ORIGINS
        - STATIC_ROOT y whitenoise storage
        """
        from django.conf import settings
        self.assertTrue(any('.onrender.com' in host for host in settings.ALLOWED_HOSTS))
        self.assertTrue(any('onrender.com' in origin for origin in settings.CSRF_TRUSTED_ORIGINS))
        self.assertTrue(settings.STATIC_ROOT is not None)
        self.assertIn('whitenoise.middleware.WhiteNoiseMiddleware', settings.MIDDLEWARE)

    def test_index_has_whatsapp_transfer_modal_and_pinterest(self):
        """
        Verifica que la plantilla index.html contenga el modal de transferencia directa a WhatsApp
        y el panel buscador integrado de Pinterest.
        """
        response = self.client.get(reverse('customizer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="whatsapp-transfer-modal"')
        self.assertContains(response, 'id="btn-open-wa-direct"')
        self.assertContains(response, 'id="pinterest-search-input"')
        self.assertContains(response, 'id="btn-search-pinterest"')






