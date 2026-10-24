"""
StampCol - Motor Dinámico de Generación de Estampados DTF & Streetwear
Crea gráficos vectoriales (SVG) de alta definición en tiempo real, 
100% aislados (fondo transparente sin cajas opacas) y optimizados para DTF textil,
adaptando la paleta de contraste según el color de la camiseta elegida (Blanco o Negro).
"""

import base64
import re
import html


def clean_text_for_title(prompt, max_len=26):
    """Limpia el prompt del usuario para extraer una frase o título legible."""
    if not prompt:
        return "STAMPCOL CUSTOM"
    
    # Remover coletillas comunes de consulta en chat
    text = prompt.strip()
    patterns_to_remove = [
        r'^(reg[aá]lame|dame|quiero|quieroun|hazme|crea|dise[ñn]a|haz|podr[íi]as hacer|pon|necesito)\s+(un[a]?\s+)?(dise[ñn]o\s+)?(de\s+)?(para\s+)?',
        r'^(un[a]?\s+)?(arbol|árbol|imagen|dibujo|estampado|dise[ñn]o|logo)\s+(de\s+|para\s+)?',
        r'^(una\s+idea\s+(de\s+)?(para\s+)?)',
        r'^(idea\s+de\s+dise[ñn]o\s+para\s+)',
        r'^(un\s+estampado\s+(de\s+|para\s+)?)',
        r'^(algo\s+(de\s+|para\s+)?)'
    ]
    for p in patterns_to_remove:
        text = re.sub(p, '', text, flags=re.IGNORECASE).strip()

    # Si hay comillas en el prompt, priorizar lo que está entre comillas
    quote_match = re.search(r'["\']([^"\']+)["\']', prompt)
    if quote_match and len(quote_match.group(1).strip()) > 2:
        text = quote_match.group(1).strip()

    if not text:
        text = "STREETWEAR"

    # Truncar con elegancia si es muy largo
    if len(text) > max_len:
        words = text.split()
        short = ""
        for w in words:
            if len(short + " " + w) <= max_len:
                short = (short + " " + w).strip()
            else:
                break
        text = short if short else text[:max_len]

    return text.upper()


def generate_dynamic_stamp(user_prompt, shirt_color='Blanco'):
    """
    Analiza el texto ingresado por el cliente y genera un estampado profesional de ilustración,
    100% aislado (fondo transparente) y con contraste óptimo para la camiseta seleccionada.
    NUNCA imprime el mensaje del usuario como texto en un banner a menos que solicite expresamente frases.
    """
    p = (user_prompt or '').lower()
    title_text = html.escape(clean_text_for_title(user_prompt, max_len=24))
    is_light = (shirt_color or 'blanco').lower() in ['blanco', 'white', 'gris', 'beige', 'amarillo', 'arena', 'blanco test']

    # 1. ÁRBOL / NATURALEZA / BONSAI / SAKURA / BOSQUE / FLORES / PLANTAS
    if any(k in p for k in ['arbol', 'árbol', 'bonsai', 'cerezo', 'sakura', 'naturaleza', 'bosque', 'selva', 'planta', 'hoja', 'flora', 'arboles', 'árboles', 'ramas', 'jardin', 'jardín', 'botanic']):
        svg = _build_tree_nature_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Árbol Místico Sagrado (Bonsai Zen)',
            'concept': 'Ilustración botánica streetwear de autor con árbol sagrado, ramas orgánicas, follaje en capas y aura zen circular para estampación DTF Ultra HD.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 2. ANIME / CYBERPUNK / GUERRERO / FIGHTER / MANGA / STREETWEAR
    elif any(k in p for k in ['anime', 'cyber', 'manga', 'guerrer', 'fighter', 'luchador', '2077', 'futurist', 'robot', 'mecha', 'shinobi', 'chica anime', 'otaku']):
        return {
            'stamp_url': '/static/customizer/images/samples/streetwear_anime.png',
            'title': f'Streetwear Anime Fighter 2077 ({title_text})',
            'concept': 'Ilustración manga cyberpunk con trazo vectorial de alta definición, kanjis perimetrales y contrastes en neón púrpura y cian listos para DTF.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 3. DRAGÓN / ORIENTAL / JAPONÉS / MINIMALISTA
    elif any(k in p for k in ['dragón', 'dragon', 'oriental', 'samurai', 'sol naciente', 'japones', 'japonés']):
        return {
            'stamp_url': '/static/customizer/images/samples/dragon_minimal.png',
            'title': f'Dragón Minimalista Japonés ({title_text})',
            'concept': 'Ilustración en tinta asiática con dragón oriental estilizado, sol carmesí y nubes flotantes en trazo vectorial puro sin fondo.',
            'placement': 'front',
            'suggested_color': '#FFFFFF',
            'suggested_color_name': 'Blanco'
        }

    # 4. CALAVERA / SKULL / GAMER
    elif any(k in p for k in ['calavera', 'skull', 'gamer', 'esqueleto', 'muerte', 'gaming']):
        return {
            'stamp_url': '/static/customizer/images/samples/cyber_skull.svg',
            'title': f'Cyber Skull Neon DTF ({title_text})',
            'concept': 'Composición de calavera cyberpunk con degradados neón cian-magenta, ojos brillantes y tipografía urbana de impacto.',
            'placement': 'front',
            'suggested_color': '#121212',
            'suggested_color_name': 'Negro'
        }

    # 5. COCHES / AUTOS / MOTOS / RACING / DRIFT
    elif any(k in p for k in ['carro', 'auto', 'coche', 'moto', 'motocicleta', 'carrera', 'racing', 'drift', 'vehiculo', 'vehículo', 'supercar', 'motor', 'bmw', 'porsche']):
        svg = _build_car_racing_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'GT Supercar Street Racing',
            'concept': 'Silueta aerodinámica de auto deportivo urbano con líneas de velocidad y estética drift optimizada para textil DTF.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 6. ESPACIO / ASTRONAUTA / GALAXIA / COSMOS
    elif any(k in p for k in ['astronauta', 'espacio', 'galaxia', 'planeta', 'cosmos', 'universo', 'alien', 'luna', 'cohete', 'nasa', 'estrella']):
        svg = _build_space_astronaut_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Cosmic Astronaut Explorer',
            'concept': 'Ilustración de astronauta interestelar con visor holográfico, órbitas cósmicas y estética streetwear espacial.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 7. MÚSICA / GUITARRA / ROCK / DJ / AUDIO
    elif any(k in p for k in ['musica', 'música', 'guitarra', 'rock', 'dj', 'audio', 'sonido', 'cancion', 'canción', 'auricular', 'vinilo']):
        svg = _build_music_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Electric Rock Soundwaves',
            'concept': 'Composición de guitarra eléctrica y frecuencias sonoras en trazo vectorial de autor con contraste para DTF.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 8. TIPOGRAFÍA / FRASE / ESPALDA / VINTAGE / QUOTE (SOLO SI EL USUARIO PIDE EXPRESAMENTE FRASES O TEXTO)
    elif any(k in p for k in ['frase', 'espalda', 'tipograf', 'quote', 'letras', 'texto', 'create your idea', 'create your reality', 'coordenadas', 'palabra', 'escriba']):
        placement = 'back' if any(k in p for k in ['espalda', 'back', 'trasera']) else 'front'
        return {
            'stamp_url': '/static/customizer/images/samples/streetwear_typography.png',
            'title': f'Urban Streetwear Typography ({title_text})',
            'concept': 'Composición tipográfica streetwear industrial de alto contraste con código de barras, coordenadas y estética de estudio contemporáneo.',
            'placement': placement,
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Blanco'
        }

    # 9. RETRO / SUNSET / 80s / SYNTHWAVE / PALMERAS
    elif any(k in p for k in ['retro', 'sunset', '80s', 'synthwave', 'vaporwave', 'palmera', 'miami', 'playa']):
        return {
            'stamp_url': '/static/customizer/images/samples/retro_sunset.svg',
            'title': f'Retro Synthwave Sunset ({title_text})',
            'concept': 'Puesta de sol ochentera con siluetas de palmeras tropicales, rejilla retroiluminada y degradados cromáticos listos para DTF.',
            'placement': 'front',
            'suggested_color': '#121212',
            'suggested_color_name': 'Negro'
        }

    # 10. OLA / THE GREAT WAVE / MAR / OCÉANO
    elif any(k in p for k in ['ola', 'wave', 'mar', 'océano', 'oceano', 'surf', 'tsunami']):
        return {
            'stamp_url': '/static/customizer/images/samples/tokyo_wave.svg',
            'title': f'The Great Tokyo Wave ({title_text})',
            'concept': 'La gran ola estilizada en grabado vectorial limpio con sol carmesí y sello tradicional japonés para prendas de autor.',
            'placement': 'front',
            'suggested_color': '#FFFFFF',
            'suggested_color_name': 'Blanco'
        }

    # 11. MINDSET / GYM / MOTIVACIÓN / FITNESS
    elif any(k in p for k in ['mindset', 'gym', 'fitness', 'motivacion', 'motivación', 'crossfit', 'disciplina', 'entren']):
        return {
            'stamp_url': '/static/customizer/images/samples/mindset_quote.svg',
            'title': f'Mindset Athletic ({title_text})',
            'concept': 'Insignia atlética motivacional con tipografía deportiva de impacto, estrellas de rendimiento y acabado vectorial sin fondo.',
            'placement': 'front',
            'suggested_color': '#121212',
            'suggested_color_name': 'Negro'
        }

    # 12. DEPORTES / FÚTBOL / ESCUDO
    elif any(k in p for k in ['fútbol', 'futbol', 'equipo', 'campeon', 'torneo', 'fc', 'club', 'deport']):
        svg = _build_sports_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Escudo Deportivo Champions',
            'concept': 'Emblema deportivo heráldico con laureles de victoria, estrellas de campeonato, cintas atléticas y trazo limpio sin fondo para DTF.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 13. MASCOTAS / FAUNA (Perro, Gato, León, Lobo, etc.)
    elif any(k in p for k in ['perro', 'gato', 'mascota', 'león', 'leon', 'lobo', 'oso', 'águila', 'aguila', 'toro', 'tigre', 'pantera']):
        svg = _build_animal_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Wildlife Streetwear Spirit',
            'concept': 'Silueta estilizada de fauna con corona de gloria, contornos vectoriales dobles y estética de autor sobre fondo transparente.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 14. EMPRESA / NEGOCIO / LOGO / BARBERÍA / CAFÉ
    elif any(k in p for k in ['empresa', 'logo', 'negocio', 'corporat', 'marca', 'barber', 'restaurante', 'cafeter', 'café', 'taller']):
        svg = _build_corporate_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Insignia Corporativa Premium',
            'concept': 'Insignia corporativa moderna con hexágono calado, estrella central, acentos dorados y tipografía sobria para uniformes de dotación.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }

    # 15. AMOR / PAREJA / ANIVERSARIO
    elif any(k in p for k in ['amor', 'aniversario', 'pareja', 'novi', 'espos', 'boda', 'familia', 'mamá', 'mama', 'papá', 'papa']):
        svg = _build_love_anniversary_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Forever Love Special Edition',
            'concept': 'Emblema conmemorativo con corazón en trazos limpios de rosa carmesí, laureles de unión y tipografía de autor sin recuadro de fondo.',
            'placement': 'front',
            'suggested_color': '#FFFFFF',
            'suggested_color_name': 'Blanco'
        }

    # 16. GENERAL / CUALQUIER OTRA IDEA LIBRE ESCRITA EN EL CHAT
    else:
        svg = _build_general_streetwear_svg(is_light)
        return {
            'stamp_url': _svg_to_data_uri(svg),
            'title': 'Streetwear Culture DTF',
            'concept': 'Gráfico urbano de autor con corona de precisión, kanjis de diseño estilizados y 100% fondo transparente sin recuadros opacos.',
            'placement': 'front',
            'suggested_color': '#FFFFFF' if is_light else '#121212',
            'suggested_color_name': shirt_color or 'Negro'
        }


def _svg_to_data_uri(svg_string):
    """Convierte el SVG a un data URI base64 compatible con Canvas e Image."""
    encoded = base64.b64encode(svg_string.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"


# ==============================================================================
# PLANTILLAS VECTORIALES STREETWEAR ADAPTABLES AL COLOR DE LA PRENDA
# ==============================================================================

def _build_tree_nature_svg(is_light=True):
    """Genera una ilustración vectorial botánica de un árbol sagrado/bonsai sin fondo opaco."""
    trunk_color = "#3E2723" if is_light else "#D97706"
    leaf_c1 = "#15803D" if is_light else "#22C55E"
    leaf_c2 = "#16A34A" if is_light else "#4ADE80"
    leaf_c3 = "#047857" if is_light else "#10B981"
    ring_color = "#DC2626" if is_light else "#F43F5E"
    text_color = "#0F172A" if is_light else "#FFFFFF"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <!-- Sol Zen Oriental y Aro Calado Exterior (Fondo 100% transparente) -->
    <circle cx="300" cy="260" r="190" fill="none" stroke="{ring_color}" stroke-width="7"/>
    <circle cx="300" cy="260" r="172" fill="none" stroke="{ring_color}" stroke-width="2" stroke-dasharray="8 6" opacity="0.6"/>
    <circle cx="300" cy="230" r="115" fill="{ring_color}" opacity="0.18"/>

    <!-- Raíces del Árbol de la Vida -->
    <g fill="none" stroke="{trunk_color}" stroke-linecap="round">
        <path d="M300 410 C 300 440, 260 465, 210 475" stroke-width="8"/>
        <path d="M290 415 C 270 445, 235 460, 185 465" stroke-width="5"/>
        <path d="M300 410 C 300 440, 340 465, 390 475" stroke-width="8"/>
        <path d="M310 415 C 330 445, 365 460, 415 465" stroke-width="5"/>
        <path d="M300 420 L 300 480" stroke-width="6"/>
    </g>

    <!-- Tronco Principal Esculpido Estilo Bonsai de Autor -->
    <path d="M280 415 C 275 340, 260 295, 290 235 C 300 215, 280 175, 300 125 C 320 175, 300 215, 310 235 C 340 295, 325 340, 320 415 Z" fill="{trunk_color}"/>
    <path d="M285 265 C 240 245, 200 255, 160 225 C 180 220, 220 230, 275 250 Z" fill="{trunk_color}"/>
    <path d="M315 265 C 360 245, 400 255, 440 225 C 420 220, 380 230, 325 250 Z" fill="{trunk_color}"/>
    <path d="M295 205 C 260 175, 220 165, 180 145 C 210 150, 250 165, 290 190 Z" fill="{trunk_color}"/>
    <path d="M305 205 C 340 175, 380 165, 420 145 C 390 150, 350 165, 310 190 Z" fill="{trunk_color}"/>

    <!-- Follaje en Capas Esféricas Zen -->
    <!-- Copa Central Superior -->
    <ellipse cx="300" cy="115" rx="65" ry="38" fill="{leaf_c1}"/>
    <ellipse cx="280" cy="100" rx="45" ry="28" fill="{leaf_c2}"/>
    <ellipse cx="320" cy="110" rx="40" ry="24" fill="{leaf_c3}"/>

    <!-- Ramas Superiores -->
    <ellipse cx="180" cy="145" rx="55" ry="32" fill="{leaf_c1}"/>
    <ellipse cx="165" cy="135" rx="40" ry="24" fill="{leaf_c2}"/>
    <ellipse cx="420" cy="145" rx="55" ry="32" fill="{leaf_c1}"/>
    <ellipse cx="435" cy="135" rx="40" ry="24" fill="{leaf_c2}"/>

    <!-- Ramas Medias -->
    <ellipse cx="150" cy="220" rx="60" ry="35" fill="{leaf_c2}"/>
    <ellipse cx="135" cy="210" rx="45" ry="24" fill="{leaf_c1}"/>
    <ellipse cx="450" cy="220" rx="60" ry="35" fill="{leaf_c2}"/>
    <ellipse cx="465" cy="210" rx="45" ry="24" fill="{leaf_c1}"/>

    <!-- Volúmenes Internos -->
    <ellipse cx="230" cy="195" rx="50" ry="30" fill="{leaf_c3}"/>
    <ellipse cx="370" cy="195" rx="50" ry="30" fill="{leaf_c3}"/>

    <!-- Kanjis Tradicionales de Naturaleza y Vida -->
    <text x="300" y="525" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="24" fill="{ring_color}" text-anchor="middle" letter-spacing="6">
        SACRED TREE · 自然
    </text>
    <text x="300" y="555" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="12" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        BOTANICAL APPAREL • STAMPCOL DTF
    </text>
</svg>"""


def _build_car_racing_svg(is_light=True):
    """Genera una ilustración automotriz streetwear de alta velocidad sin recuadro."""
    accent_color = "#EA580C" if is_light else "#06B6D4"
    stroke_color = "#DC2626" if is_light else "#F59E0B"
    text_color = "#0F172A" if is_light else "#FFFFFF"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <!-- Círculo de Velocidad y Cuadrícula Drift -->
    <circle cx="300" cy="270" r="185" fill="none" stroke="{accent_color}" stroke-width="6"/>
    <circle cx="300" cy="270" r="165" fill="none" stroke="{stroke_color}" stroke-width="2" stroke-dasharray="10 8"/>

    <!-- Líneas de velocidad dinámicas -->
    <line x1="80" y1="360" x2="520" y2="360" stroke="{stroke_color}" stroke-width="3" stroke-dasharray="16 8"/>
    <line x1="120" y1="380" x2="480" y2="380" stroke="{accent_color}" stroke-width="2"/>

    <!-- Silueta de Auto Deportivo GT Calado -->
    <path d="M 140,340 L 170,280 L 250,230 L 370,230 L 440,280 L 480,310 L 490,340 Z" fill="none" stroke="{stroke_color}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M 245,240 L 290,240 L 285,280 L 195,280 Z" fill="{accent_color}" opacity="0.8"/>
    <path d="M 310,240 L 365,240 L 420,280 L 310,280 Z" fill="{accent_color}" opacity="0.8"/>

    <!-- Ruedas y Rines Deportivos -->
    <circle cx="210" cy="340" r="38" fill="none" stroke="{stroke_color}" stroke-width="8"/>
    <circle cx="210" cy="340" r="18" fill="{accent_color}"/>
    <circle cx="420" cy="340" r="38" fill="none" stroke="{stroke_color}" stroke-width="8"/>
    <circle cx="420" cy="340" r="18" fill="{accent_color}"/>

    <!-- Luces y Alerón Trasero -->
    <line x1="130" y1="285" x2="160" y2="280" stroke="{stroke_color}" stroke-width="6"/>
    <polygon points="480,315 500,320 480,325" fill="#FACC15"/>

    <!-- Tipografía de Edición Street Racing -->
    <text x="300" y="470" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="28" fill="{stroke_color}" text-anchor="middle" letter-spacing="4">
        STREET DRIFT · GT-R
    </text>
    <text x="300" y="525" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="{text_color}" text-anchor="middle" letter-spacing="5">
        HIGH PERFORMANCE APPAREL • DTF
    </text>
</svg>"""


def _build_space_astronaut_svg(is_light=True):
    """Genera una ilustración de astronauta cósmico streetwear sin recuadro."""
    neon_cyan = "#06B6D4" if is_light else "#22D3EE"
    neon_purple = "#7C3AED" if is_light else "#C084FC"
    text_color = "#0F172A" if is_light else "#FFFFFF"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <!-- Órbita Planetaria Calada y Anillo Celestial -->
    <ellipse cx="300" cy="270" rx="200" ry="90" fill="none" stroke="{neon_cyan}" stroke-width="4" stroke-dasharray="12 6" transform="rotate(-25 300 270)"/>
    <circle cx="300" cy="270" r="180" fill="none" stroke="{neon_purple}" stroke-width="6"/>

    <!-- Casco del Astronauta -->
    <path d="M 220,290 C 210,180 390,180 380,290 C 380,360 220,360 220,290 Z" fill="none" stroke="{neon_cyan}" stroke-width="8"/>
    <!-- Visor Espejado Holográfico -->
    <path d="M 245,280 C 240,210 360,210 355,280 C 355,325 245,325 245,280 Z" fill="{neon_purple}" opacity="0.85"/>
    <path d="M 260,250 C 275,235 325,235 340,250" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>

    <!-- Hombros y Traje Espacial -->
    <path d="M 180,410 C 190,340 240,320 300,320 C 360,320 410,340 420,410 Z" fill="none" stroke="{neon_cyan}" stroke-width="6"/>

    <!-- Estrellas y Planeta Lunar -->
    <circle cx="440" cy="170" r="22" fill="none" stroke="{neon_cyan}" stroke-width="3"/>
    <ellipse cx="440" cy="170" rx="36" ry="10" fill="none" stroke="{neon_cyan}" stroke-width="2" transform="rotate(20 440 170)"/>

    <text x="300" y="480" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="26" fill="{neon_cyan}" text-anchor="middle" letter-spacing="4">
        COSMIC EXPLORER · 2077
    </text>
    <text x="300" y="535" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="{text_color}" text-anchor="middle" letter-spacing="5">
        DEEP SPACE APPAREL • STAMPCOL DTF
    </text>
</svg>"""


def _build_music_svg(is_light=True):
    """Genera una ilustración musical de guitarra y sonido de alta fidelidad."""
    accent_color = "#DC2626" if is_light else "#F43F5E"
    cyan_color = "#0284C7" if is_light else "#38BDF8"
    text_color = "#0F172A" if is_light else "#FFFFFF"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <circle cx="300" cy="270" r="185" fill="none" stroke="{accent_color}" stroke-width="6"/>
    <circle cx="300" cy="270" r="165" fill="none" stroke="{cyan_color}" stroke-width="2" stroke-dasharray="8 6"/>

    <!-- Ondas de Sonido de Ecualizador Estilizadas -->
    <g fill="{cyan_color}">
        <rect x="180" y="240" width="10" height="60" rx="4"/>
        <rect x="210" y="200" width="10" height="140" rx="4"/>
        <rect x="240" y="160" width="10" height="220" rx="4"/>
        <rect x="350" y="160" width="10" height="220" rx="4"/>
        <rect x="380" y="200" width="10" height="140" rx="4"/>
        <rect x="410" y="240" width="10" height="60" rx="4"/>
    </g>

    <!-- Silueta Central de Guitarra Eléctrica Rock -->
    <path d="M 280,390 C 250,370 250,330 280,310 L 290,210 L 285,150 L 315,150 L 310,210 L 320,310 C 350,330 350,370 320,390 Z" fill="{accent_color}"/>
    <circle cx="300" cy="350" r="18" fill="#FFFFFF"/>

    <text x="300" y="475" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="28" fill="{accent_color}" text-anchor="middle" letter-spacing="4">
        ELECTRIC ROCK · SOUND
    </text>
    <text x="300" y="530" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        AUDIO APPAREL • STAMPCOL DTF
    </text>
</svg>"""


def _build_sports_svg(is_light=True):
    text_color = "#0F172A" if is_light else "#FFFFFF"
    accent_color = "#EA580C" if is_light else "#F59E0B"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <g fill="{accent_color}">
        <polygon points="300,55 306,73 325,73 310,85 315,103 300,91 285,103 290,85 275,73 294,73"/>
        <polygon points="240,75 245,90 261,90 248,100 253,115 240,105 227,115 232,100 219,90 235,90"/>
        <polygon points="360,75 365,90 381,90 368,100 373,115 360,105 347,115 352,100 339,90 355,90"/>
    </g>

    <path d="M150 120 L450 120 C450 320 300 440 300 440 C300 440 150 320 150 120 Z" fill="none" stroke="{accent_color}" stroke-width="8"/>
    <path d="M170 140 L430 140 C430 305 300 405 300 405 C300 405 170 305 170 140 Z" fill="none" stroke="{text_color}" stroke-width="3" stroke-dasharray="8 6"/>

    <circle cx="300" cy="240" r="60" fill="none" stroke="{text_color}" stroke-width="5"/>
    <polygon points="300,210 325,230 315,258 285,258 275,230" fill="{accent_color}"/>
    <line x1="300" y1="210" x2="300" y2="180" stroke="{text_color}" stroke-width="3"/>
    <line x1="325" y1="230" x2="355" y2="225" stroke="{text_color}" stroke-width="3"/>
    <line x1="315" y1="258" x2="335" y2="288" stroke="{text_color}" stroke-width="3"/>
    <line x1="285" y1="258" x2="265" y2="288" stroke="{text_color}" stroke-width="3"/>
    <line x1="275" y1="230" x2="245" y2="225" stroke="{text_color}" stroke-width="3"/>

    <path d="M190 280 Q 230 350 290 380" fill="none" stroke="{accent_color}" stroke-width="4"/>
    <path d="M410 280 Q 370 350 310 380" fill="none" stroke="{accent_color}" stroke-width="4"/>

    <path d="M80 430 L520 430 L490 505 L110 505 Z" fill="#DC2626" stroke="{accent_color}" stroke-width="4"/>
    <text x="300" y="480" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="28" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">
        CHAMPIONS
    </text>

    <text x="300" y="550" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="14" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        ATHLETIC DIVISION • STAMPCOL DTF
    </text>
</svg>"""


def _build_animal_svg(is_light=True):
    text_color = "#0F172A" if is_light else "#FFFFFF"
    accent_color = "#D97706" if is_light else "#F59E0B"
    stroke_color = "#DC2626"
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <circle cx="300" cy="270" r="180" fill="none" stroke="{accent_color}" stroke-width="6"/>
    <circle cx="300" cy="270" r="160" fill="none" stroke="{text_color}" stroke-width="2" stroke-dasharray="10 8"/>

    <path d="M300 130 L340 180 L380 160 L365 220 L410 250 L360 280 L370 330 L300 305 L230 330 L240 280 L190 250 L235 220 L220 160 L260 180 Z" 
          fill="none" stroke="{stroke_color}" stroke-width="8" stroke-linejoin="round"/>
    <polygon points="300,170 325,210 345,195 335,240 365,260 325,280 300,260 275,280 235,260 265,240 255,195 275,210" fill="{accent_color}"/>
    <ellipse cx="280" cy="245" rx="8" ry="12" fill="#FFFFFF"/>
    <ellipse cx="320" cy="245" rx="8" ry="12" fill="#FFFFFF"/>
    <circle cx="280" cy="245" r="4" fill="#000000"/>
    <circle cx="320" cy="245" r="4" fill="#000000"/>

    <path d="M100 420 L500 420 L465 495 L135 495 Z" fill="{accent_color}" stroke="{stroke_color}" stroke-width="3"/>
    <text x="300" y="470" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="28" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">
        WILD SPIRIT
    </text>
    <text x="300" y="540" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="14" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        PREMIUM WILDLIFE APPAREL • DTF
    </text>
</svg>"""


def _build_corporate_svg(is_light=True):
    text_color = "#0F172A" if is_light else "#FFFFFF"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <polygon points="300,50 510,170 510,410 300,530 90,410 90,170" fill="none" stroke="#059669" stroke-width="8"/>
    <polygon points="300,75 485,185 485,395 300,505 115,395 115,185" fill="none" stroke="#D97706" stroke-width="3" stroke-dasharray="12 6"/>

    <polygon points="300,160 315,200 355,200 323,225 335,265 300,240 265,265 277,225 245,200 285,200" fill="#D97706"/>

    <rect x="130" y="320" width="340" height="65" rx="8" fill="#059669"/>
    <text x="300" y="364" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="24" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">
        ENTERPRISE CORP
    </text>

    <text x="300" y="430" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="14" fill="{text_color}" text-anchor="middle" letter-spacing="3">
        DOTACIÓN CORPORATIVA &amp; EVENTOS
    </text>
    <text x="300" y="460" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="12" fill="#059669" text-anchor="middle" letter-spacing="4">
        CALIDAD TEXTIL CERTIFICADA • STAMPCOL
    </text>
</svg>"""


def _build_love_anniversary_svg(is_light=True):
    text_color = "#0F172A" if is_light else "#FFFFFF"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <path d="M300 380 C 300 380, 170 280, 170 190 C 170 130, 220 100, 270 130 C 290 145, 300 165, 300 165 C 300 165, 310 145, 330 130 C 380 100, 430 130, 430 190 C 430 280, 300 380, 300 380 Z" 
          fill="none" stroke="#E11D48" stroke-width="10"/>
    <path d="M300 350 C 300 350, 190 260, 190 190 C 190 145, 230 125, 270 150 C 285 160, 300 180, 300 180 C 300 180, 315 160, 330 150 C 370 125, 410 145, 410 190 C 410 260, 300 350, 300 350 Z" 
          fill="none" stroke="#F43F5E" stroke-width="3" stroke-dasharray="8 6"/>

    <polygon points="300,90 305,105 320,105 308,115 312,130 300,120 288,130 292,115 280,105 295,105" fill="#D97706"/>

    <path d="M90 410 L510 410 L480 485 L120 485 Z" fill="#BE123C" stroke="#D97706" stroke-width="3"/>
    <text x="300" y="460" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="26" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">
        FOREVER LOVE
    </text>

    <text x="300" y="535" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        ★ EDICIÓN ESPECIAL ANIVERSARIO ★
    </text>
</svg>"""


def _build_general_streetwear_svg(is_light=True):
    text_color = "#0F172A" if is_light else "#FFFFFF"
    accent_color = "#EA580C" if is_light else "#06B6D4"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
    <circle cx="300" cy="270" r="190" fill="none" stroke="{accent_color}" stroke-width="8"/>
    <circle cx="300" cy="270" r="170" fill="none" stroke="{text_color}" stroke-width="2" stroke-opacity="0.5" stroke-dasharray="10 8"/>

    <text x="300" y="160" font-family="'Arial', sans-serif" font-weight="900" font-size="34" fill="{accent_color}" text-anchor="middle">
        限定版 • 都市
    </text>

    <polygon points="300,180 320,230 370,230 330,260 345,310 300,280 255,310 270,260 230,230 280,230" fill="{accent_color}"/>
    <circle cx="300" cy="255" r="18" fill="{text_color}"/>

    <path d="M80 400 L520 400 L485 480 L115 480 Z" fill="{accent_color}" stroke="{text_color}" stroke-width="3"/>
    <text x="300" y="453" font-family="'Outfit', 'Impact', sans-serif" font-weight="900" font-size="28" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">
        ORIGINAL STREETWEAR
    </text>

    <text x="300" y="530" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="14" fill="{text_color}" text-anchor="middle" letter-spacing="4">
        STAMPCOL APPAREL • DTF STUDIO
    </text>
</svg>"""
