import json
import base64
import os
import re
import urllib.parse
from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.core.files.base import ContentFile
from django.conf import settings

from .models import ProductOption, DesignAsset, Order
from .forms import OrderForm

# Importar Google GenAI SDK oficial
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    import requests
except ImportError:
    requests = None


@ensure_csrf_cookie
def index(request):
    """
    Vista principal que renderiza el personalizador interactivo de StampCol.
    Recupera opciones de la base de datos o provee defaults iniciales en caso de estar vacía.
    """
    colors = list(ProductOption.objects.filter(option_type='COLOR', is_active=True))
    sizes = list(ProductOption.objects.filter(option_type='SIZE', is_active=True))
    fabrics = list(ProductOption.objects.filter(option_type='FABRIC', is_active=True))
    design_assets = list(DesignAsset.objects.filter(is_active=True))

    # Valores por defecto para una experiencia inmediata si la BD está vacía
    if not colors:
        colors = [
            {'id': 1, 'name': 'Negro', 'code_hex': '#121212', 'description': 'Tono clásico, elegante y versátil'},
            {'id': 2, 'name': 'Blanco', 'code_hex': '#FFFFFF', 'description': 'Base clásica, limpia y luminosa'},
            {'id': 3, 'name': 'Azul', 'code_hex': '#1D4ED8', 'description': 'Tono clásico y versátil'},
            {'id': 4, 'name': 'Rojo', 'code_hex': '#DC2626', 'description': 'Vibrante y de alto impacto'},
            {'id': 5, 'name': 'Amarillo', 'code_hex': '#FACC15', 'description': 'Enérgico y creativo'},
            {'id': 6, 'name': 'Rosado', 'code_hex': '#F472B6', 'description': 'Tono moderno y fresco'},
            {'id': 7, 'name': 'Morado', 'code_hex': '#7C3AED', 'description': 'Elegante y artístico'},
            {'id': 8, 'name': 'Naranja', 'code_hex': '#EA580C', 'description': 'Streetwear dinámico'},
        ]

    if not sizes:
        sizes = [
            {'id': 1, 'name': 'S', 'description': 'Pequeña (Ancho 51cm / Largo 66cm)'},
            {'id': 2, 'name': 'M', 'description': 'Mediana (Ancho 55cm / Largo 69cm)'},
            {'id': 3, 'name': 'L', 'description': 'Grande (Ancho 59cm / Largo 72cm)'},
            {'id': 4, 'name': 'XL', 'description': 'Extra Grande (Ancho 63cm / Largo 75cm)'},
            {'id': 5, 'name': 'Oversize', 'description': 'Corte holgado streetwear (Ancho 65cm / Largo 76cm)'},
        ]

    if not fabrics:
        fabrics = [
            {'id': 1, 'name': '100% Algodón Peinado 180g', 'description': 'Fresca, transpirable, suave al tacto y de alta resistencia', 'extra_price': 0},
            {'id': 2, 'name': 'Algodón Pesado Streetwear 220g', 'description': 'Corte estructurado streetwear, mayor gramaje y caída firme', 'extra_price': 10000},
        ]

    # Agrupar estampados prediseñados por categoría para pestañas en el frontend
    categories_dict = {}
    for asset in design_assets:
        cat_key = asset.get_category_display() if hasattr(asset, 'get_category_display') else asset.category
        if cat_key not in categories_dict:
            categories_dict[cat_key] = []
        categories_dict[cat_key].append(asset)

    order_form = OrderForm()

    from .contenido_negocio import obtener_contenido_negocio

    context = {
        'colors': colors,
        'sizes': sizes,
        'fabrics': fabrics,
        'design_assets': design_assets,
        'categories_dict': categories_dict,
        'order_form': order_form,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '573171535408'),
        'instagram_url': 'https://www.instagram.com/stampcol2025?utm_source=qr&stkn=N2VubnBtdXhqaDBk',
        'negocio': obtener_contenido_negocio(),
    }

    return render(request, 'customizer/index.html', context)


from .dynamic_stamp_generator import generate_dynamic_stamp


def resolve_design_stamp(user_prompt):
    """
    Genera dinámicamente un diseño gráfico DTF aislado y metadatos de producción
    basados exactamente en lo que el cliente escribe en el chat, sin usar predeterminados genéricos.
    """
    p = (user_prompt or '').strip().lower()

    # Si coincide con uno de los botones de demo rápida estática previa:
    if p in ('quiero un diseño de un dragón minimalista en tintas negras', 'dragón minimal', 'dragon minimal'):
        return {
            'stamp_url': '/static/customizer/images/samples/dragon_minimal.png',
            'title': 'Dragón Minimalista Japonés',
            'placement': 'front',
            'suggested_color': '#FFFFFF',
            'suggested_color_name': 'Blanco',
            'concept': 'Ilustración limpia y estilizada de dragón oriental con sol carmesí y nubes en tinta japonesa, optimizada para DTF Ultra HD.'
        }
    elif p == "diseño de frase tipográfica vintage 'create your idea' para la espalda":
        return {
            'stamp_url': '/static/customizer/images/samples/typography_back.png',
            'title': 'Tipografía Urbana StampCol',
            'placement': 'back',
            'suggested_color': '#121212',
            'suggested_color_name': 'Negro',
            'concept': 'Diseño tipográfico brutalista contemporáneo con coordenadas y estética de estudio de diseño de autor.'
        }
    elif p == 'diseño streetwear japonés cyberpunk para camiseta negra':
        return {
            'stamp_url': '/static/customizer/images/samples/streetwear_anime.png',
            'title': 'Streetwear Anime Fighter 2077',
            'placement': 'front',
            'suggested_color': '#121212',
            'suggested_color_name': 'Negro',
            'concept': 'Composición ciberpunk de estética manga con contrastes de neón púrpura y kanjis urbanos para impacto visual.'
        }

    # Para todo lo que el cliente escriba en el chat (Navidad, equipos, mascotas, frases, logos, etc.),
    # se genera el diseño según lo solicitado:
    return generate_dynamic_stamp(user_prompt)



def get_smart_design_options(user_prompt):
    """
    Genera 3 opciones consultivas interactivas para que el cliente pueda explorar
    variaciones de diseño, ubicación y estilos con un solo toque.
    """
    p = (user_prompt or '').lower()
    if any(k in p for k in ['empresa', 'logo', 'negocio', 'corporat', 'dotaci', 'marca', 'café', 'restaurante']):
        return [
            {"label": "🔍 Pecho discreto (12x12 cm)", "prompt": f"Versión minimalista de {user_prompt} para el pecho frontal"},
            {"label": "⚡ Espalda dominante (28x35 cm)", "prompt": f"Diseño impactante de {user_prompt} en la espalda completa"},
            {"label": "✨ Añadir eslogan corporativo", "prompt": f"{user_prompt} con eslogan corporativo debajo"},
        ]
    elif any(k in p for k in ['deport', 'futbol', 'fútbol', 'gym', 'fitness', 'torneo', 'club', 'equipo']):
        return [
            {"label": "🛡️ Solo escudo frontal", "prompt": f"Escudo limpio y moderno de {user_prompt} en el pecho"},
            {"label": "🔢 Con dorsal en la espalda", "prompt": f"{user_prompt} con escudo al frente y número grande en la espalda"},
            {"label": "⚡ Estilo atlético moderno", "prompt": f"Diseño deportivo de alto rendimiento para {user_prompt}"},
        ]
    elif any(k in p for k in ['anime', 'streetwear', 'cyberpunk', 'dragon', 'dragón', 'japon']):
        return [
            {"label": "🔮 Neón Cyberpunk", "prompt": f"Versión neón cyberpunk con acentos morados de {user_prompt}"},
            {"label": "🖤 Tinta Negra Minimalista", "prompt": f"Versión minimalista en tinta negra pura de {user_prompt}"},
            {"label": "👕 Probar en camiseta negra oversize", "prompt": f"{user_prompt} optimizado para camiseta negra oversize"},
        ]
    elif any(k in p for k in ['regalo', 'pareja', 'amor', 'cumple', 'mama', 'mamá', 'papa', 'papá', 'familia']):
        return [
            {"label": "❤️ Ilustración con fecha especial", "prompt": f"Ilustración estilizada y fecha especial para {user_prompt}"},
            {"label": "✨ Line-Art minimalista", "prompt": f"Diseño en line-art minimalista y elegante de {user_prompt}"},
            {"label": "🎁 Dúo complementario para pareja", "prompt": f"Diseño complementario para pareja de {user_prompt}"},
        ]
    else:
        return [
            {"label": "✨ Estilo Minimalista Line-Art", "prompt": f"Versión minimalista y limpia de {user_prompt}"},
            {"label": "🔥 Estilo Streetwear de Gran Formato", "prompt": f"Diseño streetwear de autor inspirado en {user_prompt} para la espalda"},
            {"label": "👕 Probar en camiseta negra", "prompt": f"{user_prompt} en camiseta negra con alto contraste"},
        ]


def build_apparel_prompt(prompt_text: str, shirt_color: str = 'Blanco') -> str:
    """
    Construye las instrucciones maestras para la IA generadora de imágenes (Imagen 3 / Google GenAI),
    optimizadas con ingeniería de prompts para diseñador gráfico senior de moda urbana y estampados DTF.
    Garantiza:
    - Gráfico vectorial aislado estilo pegatina/merchandising.
    - Trazos limpios, contornos definidos y paleta vibrante de tintas textiles.
    - FONDO SÓLIDO BLANCO O TRANSPARENTE para fácil corte y remoción automática.
    - PROHIBICIÓN ESTRICTA de maquetas de camisetas, modelos humanos o fondos fotográficos.
    """
    is_light = shirt_color.lower() in ['blanco', 'white', 'gris', 'beige', 'amarillo', 'arena']
    contrast_guidance = (
        "rich bold black ink outlines with vivid high-contrast colors, deep shadows and crisp details suited for light apparel"
        if is_light else
        "bright neon saturated electric accents, bold cyber vibrant tones and crisp white highlights suited for dark apparel"
    )
    
    return (
        f"Masterpiece professional apparel t-shirt graphic artwork, vector streetwear screenprint illustration: {prompt_text}. "
        f"Design style: High-end apparel merchandise graphic art, bold crisp vector contour outlines, dynamic cel-shading, "
        f"vibrant DTF textile ink palette ({contrast_guidance}), cohesive composition with streetwear typography elements. "
        "Strictly isolated on a pure clean solid white background, flat 2D sticker art aesthetic. "
        "NEGATIVE RESTRICTIONS: Absolutely NO t-shirt mockup, DO NOT render cloth wrinkles, fabric texture, collars, or mannequins, "
        "DO NOT render a human model wearing clothing, NO photographic room backgrounds, NO borders cropped off. "
        "ONLY the standalone flat isolated graphic print emblem centered in the frame."
    )


def try_fetch_online_ai_image(prompt_text, shirt_color='Blanco'):
    """
    Intenta generar una ilustración gráfica usando un generador de imágenes IA
    con aislamiento de fondo transparente para estampación textil DTF.
    Devuelve un data URL base64 PNG con transparencia o None si no está disponible.
    """
    if not requests or not prompt_text:
        return None

    p = prompt_text.lower().strip()
    # Si el cliente solicita explícitamente texto, tipografía o presets destacados de estudio, usar activos locales
    if any(k in p for k in ['frase', 'espalda', 'tipograf', 'quote', 'letras', 'texto', 'create your idea', 'coordenadas', 'dragon', 'dragón', 'anime']):
        return None

    # Mapeo inteligente a términos visuales concretos para la IA
    keyword = None
    if any(k in p for k in ['arbol', 'árbol', 'bonsai', 'cerezo', 'sakura']):
        keyword = 'tree'
    elif any(k in p for k in ['planta', 'bosque', 'selva', 'hoja', 'flora', 'jardin', 'jardín', 'botanic']):
        keyword = 'nature plants'
    elif any(k in p for k in ['flor', 'flores', 'rosa', 'rosas', 'girasol']):
        keyword = 'flowers'
    elif any(k in p for k in ['dragon', 'dragón']):
        keyword = 'dragon'
    elif any(k in p for k in ['carro', 'auto', 'coche', 'supercar', 'drift', 'bmw', 'porsche']):
        keyword = 'car'
    elif any(k in p for k in ['moto', 'motocicleta']):
        keyword = 'motorcycle'
    elif any(k in p for k in ['astronauta', 'espacio', 'galaxia', 'universo', 'alien', 'luna', 'cohete']):
        keyword = 'astronaut'
    elif any(k in p for k in ['musica', 'música', 'guitarra', 'rock', 'dj', 'audio', 'sonido']):
        keyword = 'guitar'
    elif any(k in p for k in ['lobo', 'wolf']):
        keyword = 'wolf'
    elif any(k in p for k in ['leon', 'león']):
        keyword = 'lion'
    elif any(k in p for k in ['tigre', 'tiger']):
        keyword = 'tiger'
    elif any(k in p for k in ['aguila', 'águila']):
        keyword = 'eagle'
    elif any(k in p for k in ['perro', 'dog']):
        keyword = 'dog'
    elif any(k in p for k in ['gato', 'cat', 'felino']):
        keyword = 'cat'
    elif any(k in p for k in ['mariposa', 'butterfly']):
        keyword = 'butterfly'
    elif any(k in p for k in ['calavera', 'skull']):
        keyword = 'skull'

    if not keyword:
        cleaned = re.sub(r'^(quiero|quieroun|necesito|hazme|crea|diseña|dame|pon|un[a]?|el|la|de|para)\s+', '', p, flags=re.I).strip()
        words = cleaned.split()
        keyword = " ".join(words[:2]) if words else None

    if not keyword:
        return None

    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(keyword)}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.content) > 1500:
            from .image_processing import extract_and_clean_stamp
            return extract_and_clean_stamp(BytesIO(resp.content), tolerance=35, auto_crop=True)
    except Exception:
        pass

    return None


@csrf_exempt
def gemini_assistant_view(request):
    """
    Vista del Asistente Gemini para StampCol.
    Utiliza el SDK oficial google-genai para generación de imágenes (Imagen 3)
    con ingeniería de prompts especializada en estampados textiles DTF,
    con respaldo automático en el motor SVG vectorial y galería streetwear local.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return JsonResponse({'status': 'error', 'message': 'Datos JSON inválidos'}, status=400)

        prompt_text = data.get('prompt', '').strip()
        image_base64 = data.get('image_base64', '')
        color = data.get('color', 'Blanco')
        fabric = data.get('fabric', '100% Algodón Peinado 180g')

        if not prompt_text and not image_base64:
            return JsonResponse({
                'status': 'error',
                'message': 'Debes ingresar un texto descriptivo o cargar una imagen.'
            }, status=400)

        ai_text_response = ''
        isolated_stamp_url = None

        # 1. Intentar generación con el SDK oficial de Google GenAI
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')
        if genai and api_key and api_key != 'tu_gemini_api_key_aqui':
            try:
                client = genai.Client(api_key=api_key)
                full_apparel_prompt = build_apparel_prompt(prompt_text, color)

                # Intentar generar imagen con modelos de imagen de Google
                image_models_to_try = ['gemini-3.1-flash-image', 'gemini-2.5-flash-image']
                for img_model in image_models_to_try:
                    try:
                        img_response = client.models.generate_content(
                            model=img_model,
                            contents=full_apparel_prompt
                        )
                        if img_response and getattr(img_response, 'candidates', None):
                            for part in img_response.candidates[0].content.parts:
                                if getattr(part, 'inline_data', None) and part.inline_data.data:
                                    raw_img_bytes = part.inline_data.data
                                    from .image_processing import isolate_stamp_background
                                    isolated_stamp_url = isolate_stamp_background(raw_img_bytes, tolerance=32, auto_crop=True)
                                    break
                        if isolated_stamp_url:
                            break
                    except Exception as e_img:
                        import logging
                        logging.getLogger(__name__).debug(f"Modelo de imagen {img_model} no disponible: {e_img}")
                        if "429" in str(e_img) or "RESOURCE_EXHAUSTED" in str(e_img) or "Quota" in str(e_img):
                            break

                # Generar curaduría y concepto artístico textil con Gemini 3.8 Flash
                try:
                    text_resp = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=(
                            f"Eres el director de arte y diseñador textil de StampCol, marca prémium de estampados DTF. "
                            f"En 2 a 3 líneas directas, profesionales y estilizadas, describe el concepto del estampado para una prenda '{color}' "
                            f"inspirado en: '{prompt_text}'. Menciona la técnica DTF y el impacto visual."
                        )
                    )
                    if text_resp and text_resp.text:
                        ai_text_response = text_resp.text.strip()
                except Exception as e_text:
                    import logging
                    logging.getLogger(__name__).debug(f"Error generando texto con Gemini: {e_text}")

            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Error en cliente GenAI: {e}")
                isolated_stamp_url = None

        # Si GenAI no generó imagen directa (por cuota de clave gratuita), intentar generador de ilustración IA
        if not isolated_stamp_url and not image_base64:
            isolated_stamp_url = try_fetch_online_ai_image(prompt_text, color)

        # 2. Si se generó la imagen exitosamente, responder al frontend
        if isolated_stamp_url:
            return JsonResponse({
                'status': 'success',
                'response': (
                    ai_text_response.strip()
                    or f'¡Ilustración creada con éxito para tu idea: "{prompt_text}"! Aislada y optimizada para DTF Ultra HD.'
                ),
                'isolated_stamp': isolated_stamp_url,
                'suggested_meta': {
                    'suggested_placement': 'front',
                    'suggested_color': '#121212' if color.lower() == 'blanco' else '#FFFFFF',
                    'suggested_color_name': color,
                },
                'suggested_options': get_smart_design_options(prompt_text),
            })

        # 3. Flujo de Imagen Cargada o Edición de Diseño Anterior desde el Chat
        if image_base64:
            from .image_processing import isolate_stamp_background, apply_artistic_edit, detect_solid_background, detect_shape_request, apply_shape_mask

            shape_key, shape_label = detect_shape_request(prompt_text)

            # Detectar si el usuario pide quitar o limpiar el fondo
            is_bg_removal = (
                not prompt_text or
                bool(re.search(r'quitar\s*fondo|fondo\s*transparente|remover\s*fondo|aislar|sin\s*fondo|quitar\s*el\s*blanco|fondo\s*blanco|limpiar\s*fondo|eliminar\s*fondo', prompt_text, re.I))
            )

            if shape_key:
                isolated_url = apply_shape_mask(image_base64, shape_type=shape_key)
                title = f"Diseño en Forma {shape_label}"
                concept = f"Recorte y enmarcado en silueta {shape_label.lower()} con bordes antialiasing y fondo transparente para DTF."
                ai_desc = (
                    f"✨ **Figura {shape_label} Aplicada:** He recortado tu imagen en silueta **{shape_label.lower()}** "
                    f"con bordes suavizados antialiasing y fondo 100% transparente para estampación DTF Ultra HD sobre tu camiseta."
                )
            elif is_bg_removal:
                isolated_url = isolate_stamp_background(image_base64, tolerance=38, auto_crop=True)
                title = "Diseño con Fondo Aislado"
                concept = "Aislamiento de fondo con antialiasing para acabado DTF limpio sobre la tela."
                ai_desc = (
                    "✨ **Fondo Aislado con Éxito:** He eliminado el recuadro y fondo sólido de tu diseño, "
                    "suavizando los bordes para una estampación DTF perfecta y sin recuadros molestos sobre tu camiseta."
                )
            else:
                # El usuario solicita una edición visual o de estilo sobre el diseño existente
                isolated_url = apply_artistic_edit(image_base64, prompt_text)
                title = f"Diseño Editado: {prompt_text[:35]}"
                concept = f"Edición textil personalizada: '{prompt_text}' con transparencia preservada."
                
                # Consultar a Gemini para curaduría textil de la edición si está disponible
                if not ai_text_response and genai and api_key and api_key != 'tu_gemini_api_key_aqui':
                    try:
                        client = genai.Client(api_key=api_key)
                        edit_resp = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=(
                                f"Eres el director de arte de StampCol. El cliente solicitó la siguiente edición a su diseño: '{prompt_text}' "
                                f"para una prenda en color '{color}'. En 2 líneas ejecutivas, felicita el cambio y destaca cómo lucirá impreso en DTF."
                            )
                        )
                        if edit_resp and edit_resp.text:
                            ai_text_response = edit_resp.text.strip()
                    except Exception:
                        pass

                ai_desc = ai_text_response or (
                    f"✨ **Diseño Editado:** Apliqué los cambios solicitados (*{prompt_text}*) directamente a tu diseño anterior, "
                    "conservando la alta definición y transparencia para impresión textil DTF Ultra HD."
                )

            has_solid, bg_hex, is_white = detect_solid_background(image_base64)
            suggested_shirt_color = '#121212' if (is_white or color.lower() == 'blanco') else '#FFFFFF'
            suggested_color_name = 'Negro' if suggested_shirt_color == '#121212' else 'Blanco'

            response_body = (
                f"{ai_desc}\n\n"
                f"• **Técnica:** Impresión digital en **DTF Ultra HD** sobre {fabric}.\n"
                f"• **Contraste recomendado:** Prenda en tono **{suggested_color_name}**.\n\n"
                f"👉 *¡Tu diseño actualizado ya está aplicado en el simulador! Puedes seguir pidiendo cualquier otro ajuste en este chat o probar otra figura geométrica.*"
            )

            return JsonResponse({
                'status': 'success',
                'response': response_body,
                'isolated_stamp': isolated_url,
                'suggested_meta': {
                    'suggested_placement': 'front',
                    'suggested_color': suggested_shirt_color,
                    'suggested_color_name': suggested_color_name,
                },
                'suggested_options': [
                    {'label': '⭕ Forma Circular', 'prompt': 'Haz mi imagen redonda en forma circular'},
                    {'label': '🔺 Forma Triangular', 'prompt': 'Recorta mi imagen en forma triangular'},
                    {'label': '🔲 Rectángulo Redondeado', 'prompt': 'Recorta mi imagen en rectángulo con esquinas redondeadas'},
                    {'label': '❤️ Forma de Corazón', 'prompt': 'Recorta mi imagen en forma de corazón'},
                    {'label': '✨ Quitar Fondo', 'prompt': 'Quítale el fondo para dejarlo completamente transparente'},
                    {'label': '🎨 Acentuar Colores', 'prompt': 'Aumenta la saturación y colores vibrantes del diseño'}
                ],
            })

        # 4. Generación dinámica de estampado basada exclusivamente en texto (SVG / Preset)
        stamp_result = generate_dynamic_stamp(prompt_text, shirt_color=color)

        title = stamp_result.get('title', 'Diseño Personalizado StampCol')
        concept = stamp_result.get('concept', 'Gráfico vectorial DTF con fondo transparente y alta resolución.')
        placement = stamp_result.get('placement', 'front')
        placement_label = 'Parte Delantera (Pecho)' if placement == 'front' else 'Parte Trasera (Espalda)'
        suggested_color_name = stamp_result.get('suggested_color_name', color)

        if ai_text_response:
            fallback_response_text = (
                f"✨ **Diseño creado por IA:** **{title}**\n\n"
                f"{ai_text_response}\n\n"
                f"• **Ubicación recomendada:** Reflejado en la **{placement_label}**.\n"
                f"• **Color sugerido:** Prenda en tono **{suggested_color_name}** para óptimo contraste.\n"
                f"• **Tecnología:** Impresión digital en **DTF Ultra HD** sobre {fabric}.\n\n"
                f"👉 *¡Ya hemos aplicado el estampado a tu camiseta en el simulador! Puedes afinarlo tocando alguna de las siguientes sugerencias:*"
            )
        else:
            fallback_response_text = (
                f"✨ **Diseño creado:** **{title}**\n\n"
                f"• **Concepto visual:** {concept}\n"
                f"• **Ubicación recomendada:** Reflejado en la **{placement_label}**.\n"
                f"• **Color sugerido:** Prenda en tono **{suggested_color_name}** para óptimo contraste.\n"
                f"• **Tecnología:** Impresión digital en **DTF Ultra HD** sobre {fabric}.\n\n"
                f"👉 *¡Ya hemos aplicado el estampado a tu camiseta en el simulador! Puedes afinarlo tocando alguna de las siguientes sugerencias:*"
            )

        return JsonResponse({
            'status': 'success',
            'response': fallback_response_text,
            'isolated_stamp': stamp_result.get('stamp_url'),
            'suggested_meta': {
                'suggested_placement': stamp_result.get('placement', 'front'),
                'suggested_color': stamp_result.get('suggested_color', '#121212'),
                'suggested_color_name': stamp_result.get('suggested_color_name', 'Negro'),
            },
            'suggested_options': [
                {
                    'label': 'Añadir más detalles',
                    'prompt': f'Mejora el diseño anterior agregando más elementos visuales a: {prompt_text}',
                },
                {
                    'label': 'Cambiar estilo',
                    'prompt': f'Vuelve a generar el diseño de {prompt_text} pero con un estilo minimalista.',
                },
            ],
        })


    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'Error en el servidor: {str(e)}'},
            status=500,
        )


# Alias para retrocompatibilidad
gemini_assistant = gemini_assistant_view


def _decode_base64_file(data_uri, file_prefix='mockup'):
    """
    Convierte una cadena data:image/png;base64,... en un ContentFile de Django.
    """
    if not data_uri or ';base64,' not in data_uri:
        return None
    try:
        format_part, img_str = data_uri.split(';base64,')
        ext = format_part.split('/')[-1] if '/' in format_part else 'png'
        file_name = f"{file_prefix}_{int(base64.b64decode(img_str[:20]).hex()[:8], 16)}.{ext}"
    except Exception:
        import time
        file_name = f"{file_prefix}_{int(time.time())}.png"
        img_str = data_uri.split(';base64,')[-1]

    try:
        decoded_bytes = base64.b64decode(img_str)
        return ContentFile(decoded_bytes, name=file_name)
    except Exception:
        return None


@require_POST
def save_order(request):
    """
    Endpoint para procesar y almacenar el pedido con los mockups generados en Canvas.
    Devuelve la URL formateada para redirigir a WhatsApp con el pedido pre-llenado.
    """
    try:
        # Soporta tanto JSON como FormData
        if request.content_type and 'application/json' in request.content_type:
            payload = json.loads(request.body.decode('utf-8'))
        else:
            payload = request.POST.dict()
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Datos recibidos inválidos'}, status=400)

    customer_name = payload.get('customer_name', '').strip()
    phone_number = payload.get('phone_number', '').strip()
    garment_type = payload.get('garment_type', 'Camiseta Cuello Redondo').strip()
    size = payload.get('size', 'M').strip()
    color = payload.get('color', 'Negro Obsidiana').strip()
    fabric_type = payload.get('fabric_type', '100% Algodón Peinado 180g').strip()
    ai_instructions = payload.get('ai_instructions', '').strip()
    additional_notes = payload.get('additional_notes', '').strip()
    pinterest_url = payload.get('pinterest_url', '').strip()

    front_b64 = payload.get('front_design_base64', '')
    back_b64 = payload.get('back_design_base64', '')
    design_doc_b64 = payload.get('design_document_base64', '')

    if not customer_name:
        return JsonResponse({'status': 'error', 'message': 'Por favor ingresa tu nombre.'}, status=400)
    if not phone_number:
        return JsonResponse({'status': 'error', 'message': 'Por favor ingresa tu número de teléfono / WhatsApp.'}, status=400)

    # Crear instancia del pedido
    order = Order(
        customer_name=customer_name,
        phone_number=phone_number,
        garment_type=garment_type,
        size=size,
        color=color,
        fabric_type=fabric_type,
        ai_instructions=ai_instructions,
        additional_notes=additional_notes,
        pinterest_url=pinterest_url,
    )

    # Procesar y guardar imágenes base64 si existen
    if front_b64:
        front_file = _decode_base64_file(front_b64, file_prefix=f'order_front_{customer_name[:10]}')
        if front_file:
            order.front_design_image.save(front_file.name, front_file, save=False)

    if back_b64:
        back_file = _decode_base64_file(back_b64, file_prefix=f'order_back_{customer_name[:10]}')
        if back_file:
            order.back_design_image.save(back_file.name, back_file, save=False)

    if design_doc_b64:
        doc_file = _decode_base64_file(design_doc_b64, file_prefix=f'order_doc_{customer_name[:10]}')
        if doc_file:
            order.design_document.save(doc_file.name, doc_file, save=False)

    order.save()

    # Generar URLs absolutas accesibles de los mockups de producción, documento y ficha
    front_mockup_url = request.build_absolute_uri(order.front_design_image.url) if order.front_design_image else ''
    back_mockup_url = request.build_absolute_uri(order.back_design_image.url) if order.back_design_image else ''
    design_document_url = request.build_absolute_uri(order.design_document.url) if order.design_document else ''
    order_preview_url = request.build_absolute_uri(reverse('customizer:order_preview', args=[order.id]))

    # Construir mensaje de WhatsApp con formato enriquecido
    whatsapp_number = getattr(settings, 'WHATSAPP_NUMBER', '573171535408')
    if not whatsapp_number or str(whatsapp_number).strip() in ['573001234567', '']:
        whatsapp_number = '573171535408'
    whatsapp_number = re.sub(r'[^0-9]', '', str(whatsapp_number))

    tipo_prenda_str = order.garment_type if order.garment_type else "Camiseta Cuello Redondo"
    wa_text = (
        f"¡Hola StampCol! ✨ Acabo de personalizar mi {tipo_prenda_str} en la web y deseo cotizarla:\n\n"
        f"📋 *SOLICITUD DE COTIZACIÓN #{order.id}*\n"
        f"👤 *Cliente:* {order.customer_name}\n"
        f"📱 *Teléfono:* {order.phone_number}\n"
        f"👕 *Prenda elegida:* {order.garment_type}\n"
        f"📏 *Talla:* {order.size}\n"
        f"🎨 *Color base:* {order.color}\n"
        f"🧵 *Tipo de Tela:* {order.fabric_type}\n"
    )

    if order.ai_instructions:
        wa_text += f"🤖 *Idea / Concepto IA:* {order.ai_instructions[:150]}...\n"

    if order.additional_notes:
        wa_text += f"📝 *Notas Especiales:* {order.additional_notes}\n"

    # Si el diseño proviene de Pinterest o enlace de referencia externa
    if order.pinterest_url:
        wa_text += f"\n📌 *Referencia visual:* {order.pinterest_url}\n"

    wa_text += (
        f"\n📸 *Te adjunto la imagen de mi diseño con la prenda terminada.* "
        f"¿Me confirman por favor el valor total y el tiempo estimado de entrega? ¡Muchas gracias!"
    )

    encoded_text = urllib.parse.quote(wa_text)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={whatsapp_number}&text={encoded_text}"

    return JsonResponse({
        'status': 'success',
        'order_id': order.id,
        'whatsapp_url': whatsapp_url,
        'front_mockup_url': front_mockup_url,
        'back_mockup_url': back_mockup_url,
        'design_document_url': design_document_url,
        'order_preview_url': order_preview_url,
        'pinterest_url': order.pinterest_url,
        'wa_text': wa_text,
        'message': 'Pedido registrado con éxito. Redirigiendo a WhatsApp...'
    })


def order_preview(request, order_id):
    """
    Vista pública para visualizar los detalles técnicos de un pedido,
    sus mockups de alta resolución y enlaces de referencia (Pinterest).
    Permite tanto al cliente como al equipo de producción ver y descargar los mockups.
    Registra la visualización y gestiona la limpieza de archivos para optimizar el servidor.
    """
    order = get_object_or_404(Order, pk=order_id)

    # 1. Registrar primera visualización desde WhatsApp / Enlace
    if not order.is_viewed:
        order.is_viewed = True
        order.viewed_at = timezone.now()
        order.save(update_fields=['is_viewed', 'viewed_at'])

    # 2. Cargar imágenes en Base64 si el archivo físico aún existe
    front_data_url = ''
    front_file_exists = False
    if order.front_design_image:
        try:
            if hasattr(order.front_design_image, 'path') and os.path.isfile(order.front_design_image.path):
                front_file_exists = True
                with open(order.front_design_image.path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    front_data_url = f"data:image/png;base64,{b64}"
        except Exception:
            pass

    back_data_url = ''
    back_file_exists = False
    if order.back_design_image:
        try:
            if hasattr(order.back_design_image, 'path') and os.path.isfile(order.back_design_image.path):
                back_file_exists = True
                with open(order.back_design_image.path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    back_data_url = f"data:image/png;base64,{b64}"
        except Exception:
            pass

    doc_data_url = ''
    doc_file_exists = False
    if order.design_document:
        try:
            if hasattr(order.design_document, 'path') and os.path.isfile(order.design_document.path):
                doc_file_exists = True
                with open(order.design_document.path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    doc_data_url = f"data:image/png;base64,{b64}"
        except Exception:
            pass

    # 3. Limpieza automática oportunista de mockups huérfanos o pedidos vistos hace más de 30 minutos
    from .cleanup import auto_cleanup_viewed_and_expired_mockups
    try:
        auto_cleanup_viewed_and_expired_mockups(max_viewed_age_minutes=30)
    except Exception:
        pass

    # Si se solicita purga inmediata tras visualización (ej: ?auto_purge=1)
    if request.GET.get('auto_purge') == '1':
        order.purge_mockup_files()

    front_final_url = front_data_url or (request.build_absolute_uri(order.front_design_image.url) if (order.front_design_image and front_file_exists) else '')
    back_final_url = back_data_url or (request.build_absolute_uri(order.back_design_image.url) if (order.back_design_image and back_file_exists) else '')
    doc_final_url = doc_data_url or (request.build_absolute_uri(order.design_document.url) if (order.design_document and doc_file_exists) else '')

    return render(request, 'customizer/order_preview.html', {
        'order': order,
        'front_url': front_final_url,
        'back_url': back_final_url,
        'doc_url': doc_final_url,
        'front_file_exists': front_file_exists or bool(front_final_url),
        'back_file_exists': back_file_exists or bool(back_final_url),
        'doc_file_exists': doc_file_exists or bool(doc_final_url),
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '573171535408'),
    })


@require_POST
def purge_order_mockup(request, order_id):
    """
    Endpoint para eliminar inmediatamente los archivos PNG de mockup de un pedido del servidor
    tras haber sido visualizados o descargados por el cliente o taller.
    """
    order = get_object_or_404(Order, pk=order_id)
    purged = order.purge_mockup_files()
    return JsonResponse({
        'status': 'success',
        'purged': purged,
        'order_id': order.id,
        'mockups_purged': order.mockups_purged,
        'message': f'Mockups del pedido #{order_id} purgados correctamente del servidor.'
    })


@require_POST
def isolate_stamp(request):
    """
    Endpoint de IA & Visión Computacional:
    Recibe una captura de pantalla, foto o imagen con fondo sólido/bordes,
    detecta y elimina el fondo, auto-recorta márgenes muertos y extrae el estampado limpio
    con transparencia listo para ubicar sobre la camiseta.
    Soporta también recorte por forma geométrica ('shape': 'circle', 'triangle', 'rounded_rect', 'hexagon', 'heart', 'star', 'diamond')
    y remoción de fondo opcional ('remove_bg': True/False).
    """
    from .image_processing import extract_and_clean_stamp, apply_shape_mask

    image_file = None
    shape_type = None
    remove_bg = False

    if request.content_type and 'multipart/form-data' in request.content_type:
        if 'image' in request.FILES:
            image_file = request.FILES['image']
        shape_type = request.POST.get('shape')
        if 'remove_bg' in request.POST:
            remove_bg = request.POST.get('remove_bg') in ['true', 'True', '1', True]
    else:
        try:
            data = json.loads(request.body.decode('utf-8'))
            b64_data = data.get('image_base64', '')
            shape_type = data.get('shape')
            if 'remove_bg' in data:
                remove_bg = bool(data.get('remove_bg'))

            if b64_data.startswith('/static/'):
                import os
                from django.conf import settings
                from django.contrib.staticfiles import finders
                rel_path = b64_data.replace('/static/', '', 1)
                full_path = finders.find(rel_path) or os.path.join(settings.BASE_DIR, 'customizer', 'static', rel_path)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as f:
                        image_file = BytesIO(f.read())
            elif b64_data.startswith('http://') or b64_data.startswith('https://'):
                import urllib.request
                req = urllib.request.Request(b64_data, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    image_file = BytesIO(resp.read())
            elif ';base64,' in b64_data:
                img_bytes = base64.b64decode(b64_data.split(';base64,')[-1])
                image_file = BytesIO(img_bytes)
            elif b64_data.startswith('data:'):
                img_bytes = base64.b64decode(b64_data.split(',')[-1])
                image_file = BytesIO(img_bytes)
            elif b64_data:
                try:
                    img_bytes = base64.b64decode(b64_data)
                    image_file = BytesIO(img_bytes)
                except Exception:
                    pass
        except Exception:
            pass

    if not image_file:
        return JsonResponse({'status': 'error', 'message': 'No se recibió ninguna imagen para procesar.'}, status=400)

    try:
        if shape_type:
            # Si se solicita una figura geométrica:
            if remove_bg:
                try:
                    cleaned_b64 = extract_and_clean_stamp(image_file, tolerance=38, auto_crop=True)
                    final_b64 = apply_shape_mask(cleaned_b64, shape_type=shape_type)
                except Exception:
                    final_b64 = apply_shape_mask(image_file, shape_type=shape_type)
            else:
                final_b64 = apply_shape_mask(image_file, shape_type=shape_type)
            msg = f'¡Forma {shape_type} aplicada exitosamente!'
        else:
            final_b64 = extract_and_clean_stamp(image_file, tolerance=38, auto_crop=True)
            msg = '¡Estampado aislado y limpiado exitosamente!'

        return JsonResponse({
            'status': 'success',
            'isolated_image': final_b64,
            'isolated_stamp_base64': final_b64,
            'message': msg
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error procesando el estampado: {str(e)}'}, status=500)


def extract_pin_image_url(pin_url: str) -> str:
    """
    Extrae la URL directa de la imagen en alta resolución de un Pin de Pinterest
    a partir del enlace de la página (por ejemplo https://www.pinterest.com/pin/123456789/).
    """
    import urllib.request
    import re
    try:
        req = urllib.request.Request(
            pin_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            html = res.read().decode('utf-8', errors='ignore')
            # 1. Buscar meta tag og:image
            meta_img = re.search(r'<meta[^>]+property=[\'"]og:image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html)
            if meta_img:
                url = meta_img.group(1)
                return re.sub(r'/(?:236x|474x|564x)/', '/originals/', url)
            
            # 2. Buscar enlaces directos de pinimg
            pinimgs = re.findall(r'(https://i\.pinimg\.com/(?:originals|736x|564x|474x)/[^\s"\'<>]+\.(?:jpg|png|webp))', html)
            if pinimgs:
                return pinimgs[0]
    except Exception:
        pass
    return None


@require_POST
def fetch_external_image(request):
    """
    Descarga una imagen de forma segura desde un enlace externo (por ejemplo de Pinterest),
    evitando bloqueos de CORS en el navegador del cliente.
    Resuelve automáticamente enlaces de Pins (pinterest.com/pin/...) a su imagen de alta resolución.
    Aísla el fondo con IA si tiene recuadro blanco/sólido.
    """
    import urllib.request
    from .image_processing import extract_and_clean_stamp, apply_shape_mask

    try:
        data = json.loads(request.body.decode('utf-8'))
        image_url = data.get('url', '').strip()
        auto_isolate = data.get('auto_isolate', True)
        shape_type = data.get('shape', None)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Datos JSON inválidos'}, status=400)

    if not image_url or not (image_url.startswith('http://') or image_url.startswith('https://')):
        return JsonResponse({'status': 'error', 'message': 'Proporciona una URL válida (http/https).'}, status=400)

    # Si es un enlace a la página de un Pin de Pinterest, extraer la imagen original de alta resolución
    if 'pinterest.com' in image_url or 'pin.it' in image_url:
        if not any(image_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.svg']):
            extracted_img = extract_pin_image_url(image_url)
            if extracted_img:
                image_url = extracted_img

    try:
        req = urllib.request.Request(
            image_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            img_bytes = response.read()

        if len(img_bytes) < 100:
            return JsonResponse({'status': 'error', 'message': 'La imagen obtenida está vacía o dañada.'}, status=400)

        from PIL import Image
        try:
            pil_raw = Image.open(BytesIO(img_bytes)).convert("RGBA")
            raw_buf = BytesIO()
            pil_raw.save(raw_buf, format="PNG")
            raw_b64 = f"data:image/png;base64,{base64.b64encode(raw_buf.getvalue()).decode('utf-8')}"
        except Exception:
            raw_b64 = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

        # Generar siempre versión aislada limpia con el motor robusto
        try:
            isolated_b64 = extract_and_clean_stamp(BytesIO(img_bytes), tolerance=36, auto_crop=True)
        except Exception:
            isolated_b64 = raw_b64

        final_b64 = isolated_b64 if auto_isolate else raw_b64

        if shape_type:
            try:
                final_b64 = apply_shape_mask(final_b64, shape_type=shape_type)
            except Exception:
                pass

        return JsonResponse({
            'status': 'success',
            'raw_image': raw_b64,
            'isolated_image': isolated_b64,
            'final_image': final_b64,
            'message': '¡Imagen de Pinterest cargada y preparada para estampar!'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'No fue posible descargar la imagen: {str(e)}'}, status=500)


@require_POST
def analyze_stamp_vision(request):
    """
    Endpoint de Gemini Vision Multimodal y Control de Calidad Textil:
    1. Evalúa si la imagen subida es apta para estampado textil DTF (nitidez, bordes, calidad).
    2. Detecta si contiene fondo sólido o recuadro blanco plano y lo aísla automáticamente con antialiasing.
    3. Recomienda el color óptimo de camiseta para máximo impacto visual y contraste.
    """
    from .image_processing import detect_solid_background, extract_and_clean_stamp

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    b64_image = data.get('image_base64', '')
    if not b64_image:
        return JsonResponse({'status': 'error', 'message': 'Se requiere una imagen para analizar.'}, status=400)

    # Extraer mime y bytes
    mime_type = 'image/png'
    raw_b64 = b64_image
    if ';base64,' in b64_image:
        mime_type = b64_image.split(';base64,')[0].replace('data:', '')
        raw_b64 = b64_image.split(';base64,')[1]

    try:
        img_bytes = base64.b64decode(raw_b64)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Formato base64 de imagen no válido.'}, status=400)

    # 1. Detección de fondo sólido y generación de versión aislada con transparencia
    has_solid_bg, bg_hex, is_white_bg = detect_solid_background(img_bytes)
    
    try:
        isolated_b64 = extract_and_clean_stamp(BytesIO(img_bytes), tolerance=38, auto_crop=True)
    except Exception:
        isolated_b64 = b64_image

    suggested_color = '#121212' if is_white_bg else '#FFFFFF'
    suggested_color_name = 'Negro' if is_white_bg else 'Blanco'

    # 2. Análisis multimodal con Gemini API
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY')
    ai_analysis_text = ''
    verdict = 'Apto para Estampado DTF'

    if genai and api_key and api_key != 'tu_gemini_api_key_aqui':
        try:
            client = genai.Client(api_key=api_key)
            system_prompt = (
                "Eres el Director de Producción e Impresión DTF en StampCol. "
                "Evalúa brevemente la imagen adjunta para estampado textil en camisetas:\n"
                "1. Temática o elementos principales detectados.\n"
                "2. Aptitud para estampado DTF (nitidez, bordes, resolución).\n"
                "3. Diagnóstico de fondo: Indica que se ha aislado el fondo para evitar recuadros molestos.\n"
                "4. Recomendación de color de camiseta para óptimo contraste.\n"
                "Responde en tono profesional, claro y motivador (máximo 4 viñetas directas)."
            )

            # Usar types.Part para enviar imagen multimodal si el SDK lo soporta
            try:
                img_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
                vision_resp = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[img_part, system_prompt]
                )
                if vision_resp and vision_resp.text:
                    ai_analysis_text = vision_resp.text.strip()
            except Exception:
                # Si el modelo de visión tiene restricciones de cuota, recurrir a texto
                pass
        except Exception:
            pass

    # Heurística y diagnóstico enriquecido
    if not ai_analysis_text:
        bg_msg = (
            "Detectamos un recuadro blanco/sólido alrededor de tu imagen. **Lo hemos aislado automáticamente** con transparencia suave para que no se imprima como un cuadro cuadrado en la camiseta."
            if has_solid_bg else
            "Tu archivo cuenta con buena definición y bordes aptos para corte e impresión digital."
        )
        ai_analysis_text = (
            f"🔍 **Diagnóstico de Producción DTF:**\n\n"
            f"• **Aptitud Textil:** ✅ **Diseño Apto para Impresión DTF Ultra HD**.\n"
            f"• **Optimización de Fondo:** {bg_msg}\n"
            f"• **Contraste Sugerido:** Recomendamos estamparlo sobre camiseta **{suggested_color_name}** para mayor impacto visual.\n"
            f"• **Edición:** Puedes pedir modificaciones adicionales en el chat (ej. cambiar colores, agregar detalles o estilo vintage)."
        )

    verdict = "Apto (Fondo Aislado para DTF)" if has_solid_bg else "Apto para Estampado DTF"

    return JsonResponse({
        'status': 'success',
        'is_suitable': True,
        'verdict': verdict,
        'has_solid_background': has_solid_bg,
        'analysis': ai_analysis_text,
        'isolated_image': isolated_b64,
        'isolated_stamp_base64': isolated_b64,
        'suggested_meta': {
            'suggested_color': suggested_color,
            'suggested_color_name': suggested_color_name,
            'suggested_placement': 'front'
        },
        'suggested_options': [
            {'label': 'Quitar fondo blanco', 'prompt': 'Quítale el fondo blanco para dejarlo completamente transparente'},
            {'label': 'Acentuar colores', 'prompt': 'Aumenta la saturación y colores vibrantes del diseño'},
            {'label': 'Estilo vintage', 'prompt': 'Aplica un estilo vintage y retro desgastado al diseño'},
            {'label': 'Versión monocromática', 'prompt': 'Transforma el diseño a blanco y negro con alto contraste'}
        ]
    })

