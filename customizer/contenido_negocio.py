"""
StampCol - Configuración y Contenido del Negocio
Textos comerciales y de atención orientados 100% a la experiencia del cliente.
"""

from datetime import date

CONTENIDO_NEGOCIO = {
    # 1. Identidad de Marca y Localización
    'marca': 'StampCol',
    'tecnica_principal': 'DTF (Direct to Film)',
    'eslogan': 'Tu idea, tu estilo, tu camiseta. Diséñala en minutos.',
    'subtitulo_hero': 'Personalización textil con técnica DTF Ultra HD en Campoalegre, Huila. Estampa desde 1 unidad con colores vivos, tacto suave y alta resistencia al lavado.',
    
    'direccion': {
        'municipio': 'Campoalegre',
        'departamento': 'Huila',
        'pais': 'Colombia',
        'modalidad': 'Taller 100% Digital • Pedidos online y entregas a domicilio en Campoalegre y toda Colombia',
        'nota_sin_tienda': 'No contamos con tienda física abierta al público. Toda la atención, asesoría y diseño se realiza de forma personalizada vía online y WhatsApp, con entregas a domicilio.',
        'google_maps_iframe_url': 'https://maps.google.com/maps?q=Campoalegre,+Huila,+Colombia&t=&z=15&ie=UTF8&iwloc=&output=embed',
        'google_maps_link': 'https://maps.google.com/maps?q=Campoalegre,+Huila,+Colombia',
    },

    'horarios': 'Atención Online: Lunes a Sábado 8:00 AM - 7:00 PM',

    # 2. Canales de Contacto y Redes
    'whatsapp': {
        'numero': '573171535408',
        'numero_display': '317 153 5408',
        'url_base': 'https://wa.me/573171535408',
        'mensaje_general': '¡Hola StampCol! Quiero cotizar unas prendas estampadas en DTF.',
    },
    'instagram': {
        'usuario': '@stampcol2025',
        'url': 'https://www.instagram.com/stampcol2025?utm_source=qr&stkn=N2VubnBtdXhqaDBk',
    },
    'facebook': {
        'usuario': 'StampCol',
        'url': 'https://www.instagram.com/stampcol2025',
    },

    # 3. Microbeneficios del Hero
    'microbeneficios': [
        {'icono': '✨', 'titulo': 'Sin Mínimo de Pedido', 'desc': 'Estampa desde 1 sola prenda única hasta dotaciones completas.'},
        {'icono': '⚡', 'titulo': 'Entrega Rápida', 'desc': 'Producción ágil en menos de 3 días hábiles.'},
        {'icono': '🛡️', 'titulo': 'Colores que Resisten', 'desc': 'DTF Ultra HD de alta fijación con tintas textiles lavables.'},
    ],

    # 4. Barra de Confianza
    'barra_confianza': [
        {'icono': '📍', 'texto': 'Hecho en Campoalegre'},
        {'icono': '🎨', 'texto': 'Técnica Digital DTF'},
        {'icono': '🛡️', 'texto': 'Garantía de Calidad'},
        {'icono': '📦', 'texto': 'Envíos a todo Colombia'},
    ],

    # 5. Pasos de "Cómo Funciona"
    'pasos_proceso': [
        {
            'paso': '01',
            'titulo': 'Elige tu Prenda y Base',
            'desc': 'Selecciona tu color favorito, la talla adecuada y el tipo de tela que prefieras.',
            'icono': '👕'
        },
        {
            'paso': '02',
            'titulo': 'Sube tu Imagen o Crea con IA',
            'desc': 'Sube tu logo o diseño, o describe tu idea en el chat para que el asistente aísle el estampado.',
            'icono': '✨'
        },
        {
            'paso': '03',
            'titulo': 'Mira la Vista Previa Real',
            'desc': 'Previsualiza tu diseño en el frente o espalda con proporciones exactas y texturas reales.',
            'icono': '👁️'
        },
        {
            'paso': '04',
            'titulo': 'Confirma tu Pedido',
            'desc': 'Envíanos la hoja técnica con Frente y Espalda directamente por WhatsApp para producción inmediata.',
            'icono': '🚀'
        },
    ],

    # 6. Diferenciadores ("Por Qué StampCol")
    'diferenciadores': [
        {
            'titulo': 'Diseño con IA Integrado',
            'desc': 'Describe lo que imaginas o sube una captura; nuestra herramienta procesa y ubica tu estampado sin complicaciones.',
            'icono': '🧠'
        },
        {
            'titulo': 'Técnica DTF Ultra HD',
            'desc': 'Colores vivos, degradados continuos y detalle fino con acabado suave y elástico al tacto.',
            'icono': '🎨'
        },
        {
            'titulo': 'Variedad de Telas y Gramajes',
            'desc': 'DTF versátil aplicable en algodón peinado, poliéster deportivo, piel de durazno y mezclas resistentes.',
            'icono': '🧵'
        },
        {
            'titulo': 'Desde 1 Unidad',
            'desc': 'Flexibilidad total: producimos desde una pieza exclusiva para ti hasta pedidos completos para grupos y empresas.',
            'icono': '📦'
        },
        {
            'titulo': 'Producción Local y Ágil',
            'desc': 'Taller propio en Campoalegre para responder con rapidez y atención personalizada a tus requerimientos.',
            'icono': '⚡'
        },
        {
            'titulo': 'Control de Calidad Garantizado',
            'desc': 'Revisión minuciosa en confección y termofijado para garantizar que tu prenda llegue en óptimas condiciones.',
            'icono': '🛡️'
        },
    ],

    # 7. Métricas enfocadas en el cliente
    'metricas': [
        {'numero': '0', 'sufijo': 'mínimo', 'etiqueta': 'Estampa desde 1 sola prenda'},
        {'numero': '< 3', 'sufijo': 'días', 'etiqueta': 'Tiempo promedio de entrega'},
        {'numero': '4', 'sufijo': 'telas', 'etiqueta': 'Opciones textiles premium'},
        {'numero': '100', 'sufijo': '%', 'etiqueta': 'Personalizado a tu gusto'},
    ],

    # 8. Segmentos "Soluciones & Colecciones" (Formato para Slider Interactivo y Showcase Visual)
    'segmentos': [
        {
            'categoria': 'Empresas & Negocios',
            'titulo': 'Dotaciones & Uniformes Corporativos',
            'subtitulo': 'Proyecta una imagen profesional y coherente para tu equipo de trabajo.',
            'icono': '🏢',
            'imagen_preview': 'customizer/images/samples/crop_label_perfect.png',
            'placement': 'front',
            'color_hex': '#121212',
            'color_name': 'Negro',
            'badge': 'Durabilidad 50+ Lavadas',
            'puntos_clave': [
                'Logos nítidos con técnica DTF Ultra HD',
                'Resistencia comprobada a más de 50 lavadas',
                'Ubicación en pecho, espalda o mangas'
            ],
            'prenda_ideal': 'Camisetas cuello redondo en algodón peinado de alta densidad',
            'whatsapp_msg': 'Hola StampCol, requiero cotización para dotaciones empresariales con el logo de mi negocio.'
        },
        {
            'categoria': 'Moda Urbana & Creadores',
            'titulo': 'Streetwear & Marcas Propias',
            'subtitulo': 'Convierte tus ideas y diseños en colecciones con calidad boutique.',
            'icono': '🔥',
            'imagen_preview': 'customizer/images/samples/streetwear_anime.png',
            'placement': 'back',
            'color_hex': '#121212',
            'color_name': 'Negro',
            'badge': 'Tendencia Streetwear',
            'puntos_clave': [
                'Cortes clásicos y Oversize con caída pesada',
                'Estampados de gran formato en espalda sin acartonarse',
                'Colores vivos, negros puros y degradados continuos'
            ],
            'prenda_ideal': 'Algodón peinado premium 180g / 220g y cortes holgados',
            'whatsapp_msg': 'Hola StampCol, quiero cotizar prendas estilo streetwear para mi propia marca.'
        },
        {
            'categoria': 'Deportes & Clubes',
            'titulo': 'Equipos Deportivos & Torneos',
            'subtitulo': 'Uniformes completos para fútbol, microfútbol, voleibol y running.',
            'icono': '⚽',
            'imagen_preview': 'customizer/images/samples/cyber_skull.svg',
            'placement': 'front',
            'color_hex': '#1D4ED8',
            'color_name': 'Azul',
            'badge': 'Dry-Fit Alto Rendimiento',
            'puntos_clave': [
                'Telas inteligentes transpirables de secado rápido',
                'Escudos a todo color, números dorsales y nombres',
                'Precios especiales por lote para torneos'
            ],
            'prenda_ideal': 'Poliéster deportivo dry-fit de alto rendimiento',
            'whatsapp_msg': 'Hola StampCol, deseo cotizar camisetas y uniformes para un equipo deportivo.'
        },
        {
            'categoria': 'Estudiantes & Colegios',
            'titulo': 'Camisetas de Promoción & Grados',
            'subtitulo': 'Inmortaliza tu grado con camisetas confortables y diseños exclusivos.',
            'icono': '🎓',
            'imagen_preview': 'customizer/images/samples/typography_back.png',
            'placement': 'back',
            'color_hex': '#121212',
            'color_name': 'Negro',
            'badge': 'Promoción Estudiantil',
            'puntos_clave': [
                'Camisetas 100% algodón suaves, frescas y de alta durabilidad',
                'Listado de nombres y apodos con tipografía moderna',
                'Muestras digitales previas antes de confección'
            ],
            'prenda_ideal': '100% Algodón Peinado 180g o Algodón Pesado Streetwear',
            'whatsapp_msg': 'Hola StampCol, quiero cotizar camisetas de promoción para nuestro grupo estudiantil.'
        },
        {
            'categoria': 'Momentos Memorables',
            'titulo': 'Regalos Personalizados & Parejas',
            'subtitulo': 'Detalles inolvidables para cumpleaños, aniversarios y fechas especiales.',
            'icono': '🎁',
            'imagen_preview': 'customizer/images/samples/dragon_minimal.png',
            'placement': 'front',
            'color_hex': '#FFFFFF',
            'color_name': 'Blanco',
            'badge': 'Desde 1 Unidad Sin Mínimos',
            'puntos_clave': [
                'Estampa desde 1 sola prenda única sin mínimos',
                'Ilustraciones con fotos, frases o códigos de música',
                'Empaque especial listo para regalar'
            ],
            'prenda_ideal': 'Camiseta suave 100% algodón peinado en Blanco o Negro',
            'whatsapp_msg': 'Hola StampCol, quiero cotizar una prenda personalizada para un regalo especial.'
        },
        {
            'categoria': 'Eventos & Campañas',
            'titulo': 'Eventos, Ferias & Publicidad',
            'subtitulo': 'Prendas de alto impacto visual para ferias, marcas y festividades.',
            'icono': '🎉',
            'imagen_preview': 'customizer/images/samples/retro_sunset.svg',
            'placement': 'front',
            'color_hex': '#FFFFFF',
            'color_name': 'Blanco',
            'badge': 'Producción Rápida',
            'puntos_clave': [
                'Producción ágil en tiempo récord para fechas límite',
                'Colores radiantes visibles a larga distancia',
                'Despacho consolidado directo a tu lugar de evento'
            ],
            'prenda_ideal': 'Camisetas ligeras para eventos masivos y activaciones',
            'whatsapp_msg': 'Hola StampCol, solicito cotización para prendas publicitarias de un evento.'
        },
    ],

    # 9. Guía Rápida de Telas
    'guia_telas': [
        {
            'nombre': '100% Algodón Peinado',
            'subtitulo': '180g • Frescura & Suavidad Natural',
            'tacto': 'Extremadamente suave, fresco, transpirable y natural sobre la piel.',
            'ideal_para': 'Uso diario urbano, climas cálidos y templados, amantes del confort.',
            'cuidado': 'Lavar al revés con agua fría, sin blanqueador, secar a la sombra.',
            'icono': '🌿',
            'tag': 'Clásica Favorita',
            'color_theme': 'emerald'
        },
        {
            'nombre': 'Poliéster Deportivo',
            'subtitulo': 'Dry-Fit • Alto Rendimiento',
            'tacto': 'Ligero, secado ultra rápido y de alta resistencia al estiramiento.',
            'ideal_para': 'Entrenamiento, actividades deportivas y prendas de alto rendimiento.',
            'cuidado': 'Lavado suave, no requiere planchado, secado rápido al aire libre.',
            'icono': '🏃',
            'tag': 'Secado Rápido',
            'color_theme': 'sky'
        },
        {
            'nombre': 'Piel de Durazno (Peach Skin)',
            'subtitulo': 'Tacto Aterciopelado • Calidez',
            'tacto': 'Tacto aterciopelado satinado, caída fluida y sensación térmica placentera.',
            'ideal_para': 'Camisetas casuales elegantes, moda femenina y juvenil, confort.',
            'cuidado': 'Lavado delicado sin suavizante concentrado, no frotar enérgicamente.',
            'icono': '🍑',
            'tag': 'Ultra Suave',
            'color_theme': 'amber'
        },
        {
            'nombre': 'Poli-Algodón (Mezcla)',
            'subtitulo': 'Anti-Encogimiento • Uso Continuo',
            'tacto': 'Equilibrio perfecto entre la suavidad del algodón y la resistencia del poliéster.',
            'ideal_para': 'Uniformes de trabajo, dotaciones y prendas de lavado frecuente.',
            'cuidado': 'Lavado normal a máquina, plancha tibia del revés si es necesario.',
            'icono': '🧵',
            'tag': 'Alta Resistencia',
            'color_theme': 'indigo'
        },
    ],

    # 10. Cuidados de la Prenda
    'cuidados_prenda': [
        {'regla': 'Lavar siempre la prenda al revés.', 'icono': '🔄', 'titulo': 'Lavar al revés'},
        {'regla': 'Usar agua fría (máx 30°C) en ciclo suave.', 'icono': '❄️', 'titulo': 'Agua fría (máx 30°C)'},
        {'regla': 'No usar suavizantes agresivos ni cloro.', 'icono': '🚫', 'titulo': 'Cero blanqueador'},
        {'regla': 'No planchar sobre el estampado; planchar siempre del revés.', 'icono': '👔', 'titulo': 'Planchar del revés'},
        {'regla': 'Evitar secadora a alta temperatura; secar a la sombra.', 'icono': '☀️', 'titulo': 'Secado a la sombra'},
        {'regla': 'Guardar en gancho o doblada sin fricción excesiva.', 'icono': '🛡️', 'titulo': 'Cuidado al guardar'},
    ],

    # 11. Entregas y Envíos (100% Online)
    'entregas': {
        'modelo': 'Taller 100% Digital',
        'local': 'Entrega a domicilio en Campoalegre (Huila). Sin punto físico de atención para brindarte mayor rapidez y precios directos de fábrica.',
        'nacional': 'Envíos asegurados a toda Colombia con número de guía de rastreo (Interrapidísimo, Envía, Servientrega).',
        'atencion': 'Atención y asesoría técnica personalizada 100% por WhatsApp y nuestra plataforma web.',
    },

    # 11.5 Galería de Diseños Listos para Probar en el Estudio (1-Click)
    'disenos_populares': [
        {
            'id': 'dragon',
            'nombre': 'Dragón Minimal',
            'categoria': 'Arte Oriental',
            'url': '/static/customizer/images/samples/dragon_minimal.png',
            'placement': 'front',
            'color': '#FFFFFF',
            'color_name': 'Blanco',
            'scale': 0.85,
            'desc': 'Tinta oriental limpia'
        },
        {
            'id': 'streetwear',
            'nombre': 'Streetwear Cyberpunk',
            'categoria': 'Streetwear',
            'url': '/static/customizer/images/samples/streetwear_anime.png',
            'placement': 'back',
            'color': '#121212',
            'color_name': 'Negro',
            'scale': 1.15,
            'desc': 'Gran formato para espalda'
        },
        {
            'id': 'typography',
            'nombre': 'Tipografía Urbana',
            'categoria': 'Lettering',
            'url': '/static/customizer/images/samples/streetwear_typography.png',
            'placement': 'back',
            'color': '#121212',
            'color_name': 'Negro',
            'scale': 0.95,
            'desc': 'Brutalismo contemporáneo'
        },
        {
            'id': 'retro_sunset',
            'nombre': 'Retro Sunset 80s',
            'categoria': 'Vintage',
            'url': '/static/customizer/images/samples/retro_sunset.svg',
            'placement': 'front',
            'color': '#121212',
            'color_name': 'Negro',
            'scale': 0.85,
            'desc': 'Paleta vintage cálida'
        },
        {
            'id': 'cyber_skull',
            'nombre': 'Cyber Skull',
            'categoria': 'Urbano',
            'url': '/static/customizer/images/samples/cyber_skull.svg',
            'placement': 'front',
            'color': '#121212',
            'color_name': 'Negro',
            'scale': 0.85,
            'desc': 'Vector gráfico de alto impacto'
        },
        {
            'id': 'tokyo_wave',
            'nombre': 'Tokyo Wave',
            'categoria': 'Ilustración',
            'url': '/static/customizer/images/samples/tokyo_wave.svg',
            'placement': 'front',
            'color': '#FFFFFF',
            'color_name': 'Blanco',
            'scale': 0.85,
            'desc': 'Estética oriental icónica'
        },
    ],

    # 12. Preguntas Frecuentes (FAQ)
    'faqs': [
        {
            'pregunta': '¿Cuánto tiempo tarda la producción y entrega de mi prenda?',
            'respuesta': 'La mayoría de pedidos se producen y entregan en menos de 3 días hábiles. En pedidos locales en Campoalegre la entrega puede ser inmediata una vez termofijado el diseño.'
        },
        {
            'pregunta': '¿Qué cuidados debo tener para que el estampado DTF dure años?',
            'respuesta': 'El estampado DTF tiene excelente adherencia textil. Te recomendamos lavar la prenda al revés con agua fría, no usar blanqueador ni secadora caliente, y planchar siempre por el revés.'
        },
        {
            'pregunta': '¿Qué tipo de imagen puedo subir?',
            'respuesta': 'Puedes subir cualquier imagen en formato PNG o JPG, o describir lo que imaginas en el chat con IA. Para máxima nitidez, recomendamos imágenes de buena resolución.'
        },
        {
            'pregunta': '¿Puedo pedir desde 1 sola prenda?',
            'respuesta': '¡Totalmente! No exigimos mínimos de compra. Puedes personalizar una sola camiseta para ti o solicitar lotes completos para eventos, grupos y empresas.'
        },
        {
            'pregunta': '¿Cómo solicito una cotización?',
            'respuesta': 'Es muy sencillo: personaliza tu prenda en el visor interactivo y presiona "Cotizar por WhatsApp". Recibiremos la hoja técnica con tu diseño de Frente y Espalda para darte un valor exacto al instante.'
        },
        {
            'pregunta': '¿Hacen envíos fuera de Campoalegre?',
            'respuesta': '¡Sí! Realizamos envíos seguros a toda Colombia mediante transportadoras reconocidas (Interrapidísimo, Envía, Servientrega) con número de guía.'
        },
    ],

    # 13. Campaña Estacional
    'banner_temporada': {
        'activo': True,
        'titulo': '✨ Temporada Especial StampCol',
        'subtitulo': '¡Personaliza tus camisetas! Diseña en minutos y recibe en casa.',
        'fecha_inicio': '2026-01-01',
        'fecha_fin': '2026-12-31',
        'cta_texto': 'Empezar a Diseñar',
    },

    'ideas_rapidas_prompt': [
        {'emoji': '⚡', 'etiqueta': 'Anime Fighter', 'prompt': 'Diseño streetwear japonés cyberpunk anime fighter 2077 para camiseta'},
        {'emoji': '🐉', 'etiqueta': 'Dragón Minimal', 'prompt': 'Quiero un diseño de un dragón minimalista en tintas negras oriental'},
        {'emoji': '💀', 'etiqueta': 'Cyber Skull', 'prompt': 'Diseño de calavera gamer con luces neón y estética urbana DTF'},
        {'emoji': '🔥', 'etiqueta': 'Streetwear Typography', 'prompt': "Diseño tipográfico streetwear contemporáneo 'Create Your Reality' para la espalda"},
        {'emoji': '🌊', 'etiqueta': 'Great Wave', 'prompt': 'Diseño de la gran ola japonesa con sol rojo estilo streetwear'},
    ],
}


def obtener_contenido_negocio():
    contenido = dict(CONTENIDO_NEGOCIO)
    banner = contenido.get('banner_temporada', {})
    if banner and banner.get('activo'):
        hoy = date.today().isoformat()
        f_inicio = banner.get('fecha_inicio', '')
        f_fin = banner.get('fecha_fin', '')
        if f_inicio and hoy < f_inicio:
            contenido['mostrar_banner_temporada'] = False
        elif f_fin and hoy > f_fin:
            contenido['mostrar_banner_temporada'] = False
        else:
            contenido['mostrar_banner_temporada'] = True
    else:
        contenido['mostrar_banner_temporada'] = False
    return contenido
