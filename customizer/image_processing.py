import io
import base64
import math
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageChops

def extract_and_clean_stamp(image_bytes_or_file, tolerance=36, auto_crop=True):
    """
    Motor ultra-robusto de aislamiento de fondo textil DTF:
    1. Detecta el color de fondo dominante mediante estadística robusta (mediana perimetral),
       siendo 100% inmune a logotipos o estampados centrados que toquen o rocen los bordes.
    2. Realiza FloodFill conectado desde el exterior y umbralización adaptativa sin agujerear
       elementos internos (letras blancas, ojos, dientes, calaveras, brillos).
    3. Trata artefactos de compresión JPG y halos con refinamiento morfológico y antialiasing DTF.
    4. Auto-recorta márgenes vacíos para óptima ubicación en camisetas o buzos.
    """
    if isinstance(image_bytes_or_file, (str, bytes, bytearray, io.BytesIO)):
        if isinstance(image_bytes_or_file, str):
            if 'base64,' in image_bytes_or_file:
                raw_b64 = image_bytes_or_file.split('base64,')[1]
            else:
                raw_b64 = image_bytes_or_file
            img_bytes = base64.b64decode(raw_b64)
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        elif isinstance(image_bytes_or_file, (bytes, bytearray)):
            pil_img = Image.open(io.BytesIO(image_bytes_or_file)).convert("RGBA")
        else:
            pil_img = Image.open(image_bytes_or_file).convert("RGBA")
    elif isinstance(image_bytes_or_file, Image.Image):
        pil_img = image_bytes_or_file.convert("RGBA")
    else:
        pil_img = Image.open(image_bytes_or_file).convert("RGBA")

    # Redimensionar si es excesivamente grande para procesamiento ultra rápido
    max_dim = 1600
    if pil_img.width > max_dim or pil_img.height > max_dim:
        pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    w, h = pil_img.size
    if w < 4 or h < 4:
        out_buf = io.BytesIO()
        pil_img.save(out_buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(out_buf.getvalue()).decode('utf-8')}"

    rgba_arr = np.array(pil_img)
    rgb_arr = rgba_arr[:, :, :3]
    orig_alpha = rgba_arr[:, :, 3]

    # Verificar si ya viene con transparencia significativa en bordes
    perimeter_alphas = np.concatenate([
        orig_alpha[0, :], orig_alpha[h - 1, :],
        orig_alpha[:, 0], orig_alpha[:, w - 1]
    ])
    if np.mean(perimeter_alphas < 30) > 0.40:
        # Ya tiene fondo transparente
        if auto_crop:
            bbox = pil_img.getbbox()
            if bbox:
                pad = 6
                pil_img = pil_img.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad)))
        out_buf = io.BytesIO()
        pil_img.save(out_buf, format="PNG", optimize=True)
        return f"data:image/png;base64,{base64.b64encode(out_buf.getvalue()).decode('utf-8')}"

    # 1. Muestreo perimetral continuo con franja de seguridad de 2 a 3px
    strip_size = max(1, min(3, min(h, w) // 20))
    top_strip = rgb_arr[:strip_size, :, :].reshape(-1, 3)
    bottom_strip = rgb_arr[-strip_size:, :, :].reshape(-1, 3)
    left_strip = rgb_arr[:, :strip_size, :].reshape(-1, 3)
    right_strip = rgb_arr[:, -strip_size:, :].reshape(-1, 3)
    
    perimeter_colors = np.concatenate([top_strip, bottom_strip, left_strip, right_strip], axis=0)
    bg_median = np.median(perimeter_colors, axis=0)
    bg_r, bg_g, bg_b = bg_median[0], bg_median[1], bg_median[2]

    bgr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
    is_white_bg = bool(bg_r > 215 and bg_g > 215 and bg_b > 215)
    is_black_bg = bool(bg_r < 40 and bg_g < 40 and bg_b < 40)

    # 2. Configurar semillas de inundación conectada exterior (FloodFill con rango fijo)
    # IMPORTANTE: FLOODFILL_FIXED_RANGE evita que el floodfill compare vecino-a-vecino y se filtre
    # a través de degradados o bordes antialiasing hacia el estampado o logotipo.
    mask = np.zeros((h + 2, w + 2), np.uint8)

    lo_diff = int(tolerance * 0.8)
    up_diff = int(tolerance * 0.8)
    if is_white_bg:
        lo_diff = min(32, max(25, lo_diff))
        up_diff = min(32, max(25, up_diff))
    elif is_black_bg:
        lo_diff = min(28, max(20, lo_diff))
        up_diff = min(28, max(20, up_diff))
    else:
        lo_diff = min(30, max(22, lo_diff))
        up_diff = min(30, max(22, up_diff))

    seeds = []
    # Esquinas externas e intermedias
    seeds.extend([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])
    seeds.extend([(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)])
    # Muestras espaciadas a lo largo de los 4 bordes exteriores
    num_samples = max(8, min(24, max(w, h) // 30))
    for step in range(1, num_samples):
        x_pt = int(w * step / num_samples)
        y_pt = int(h * step / num_samples)
        seeds.append((x_pt, 0))
        seeds.append((x_pt, h - 1))
        seeds.append((0, y_pt))
        seeds.append((w - 1, y_pt))

    diff_tuple = (lo_diff, lo_diff, lo_diff)

    for sx, sy in seeds:
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))
        if mask[sy + 1, sx + 1] == 0:
            pt_col = rgb_arr[sy, sx].astype(float)
            dist_to_bg = np.linalg.norm(pt_col - bg_median)
            # Solo inundar desde semillas coherentes con el fondo dominante
            if dist_to_bg <= 28.0:
                cv2.floodFill(
                    bgr, mask, (sx, sy), (0, 0, 0),
                    loDiff=diff_tuple, upDiff=diff_tuple,
                    flags=4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8)
                )

    # Máscara binaria del fondo exterior conectado
    bg_mask = (mask[1:h + 1, 1:w + 1] == 255)

    # 3. Refuerzo para halos JPG casi blancos adyacentes al fondo exterior
    if is_white_bg:
        dist_white = np.sqrt(
            (255.0 - rgb_arr[:, :, 0].astype(float))**2 +
            (255.0 - rgb_arr[:, :, 1].astype(float))**2 +
            (255.0 - rgb_arr[:, :, 2].astype(float))**2
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated_bg = cv2.dilate(bg_mask.astype(np.uint8), kernel) == 1
        bg_mask = bg_mask | ((dist_white < 24.0) & dilated_bg)
    elif is_black_bg:
        dist_black = np.sqrt(
            rgb_arr[:, :, 0].astype(float)**2 +
            rgb_arr[:, :, 1].astype(float)**2 +
            rgb_arr[:, :, 2].astype(float)**2
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated_bg = cv2.dilate(bg_mask.astype(np.uint8), kernel) == 1
        bg_mask = bg_mask | ((dist_black < 22.0) & dilated_bg)

    fg_mask = ~bg_mask

    # 4. Generación de mapa alfa nítido con antialiasing sutil DTF
    raw_alpha = np.where(fg_mask, 255.0, 0.0).astype(np.float32)
    smooth_alpha = cv2.GaussianBlur(raw_alpha, (3, 3), 0.7)
    final_alpha = np.clip(smooth_alpha, 0, 255).astype(np.uint8)
    final_alpha = np.minimum(final_alpha, orig_alpha)

    result_rgba = np.dstack((rgb_arr, final_alpha))
    isolated_img = Image.fromarray(result_rgba, mode="RGBA")

    # 5. Auto-recorte inteligente de márgenes vacíos
    if auto_crop:
        bbox = isolated_img.getbbox()
        if bbox:
            pad = 6
            x0 = max(0, bbox[0] - pad)
            y0 = max(0, bbox[1] - pad)
            x1 = min(w, bbox[2] + pad)
            y1 = min(h, bbox[3] + pad)
            isolated_img = isolated_img.crop((x0, y0, x1, y1))

    # Realce sutil de color para DTF
    try:
        color_enhancer = ImageEnhance.Color(isolated_img)
        isolated_img = color_enhancer.enhance(1.05)
    except Exception:
        pass

    out_buffer = io.BytesIO()
    isolated_img.save(out_buffer, format="PNG", optimize=True)
    b64_str = base64.b64encode(out_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"


def isolate_stamp_background(image_data_or_bytes, tolerance=35, auto_crop=True):
    """
    Wrapper polimórfico para aislar el estampado a partir de bytes binarios,
    archivo abierto, string base64 puro o Data URI (data:image/png;base64,...).
    """
    if isinstance(image_data_or_bytes, str):
        if 'base64,' in image_data_or_bytes:
            raw_b64 = image_data_or_bytes.split('base64,')[1]
        else:
            raw_b64 = image_data_or_bytes
        img_bytes = base64.b64decode(raw_b64)
        input_file = io.BytesIO(img_bytes)
    elif isinstance(image_data_or_bytes, (bytes, bytearray)):
        input_file = io.BytesIO(image_data_or_bytes)
    else:
        input_file = image_data_or_bytes
    return extract_and_clean_stamp(input_file, tolerance=tolerance, auto_crop=auto_crop)


def detect_solid_background(image_data_or_bytes):
    """
    Detecta si una imagen tiene un fondo sólido/plano (como un recuadro blanco o negro)
    que requiera aislamiento para estampado textil DTF.
    Utiliza estadística perimetral continua y clustering para ser inmune a diseños que toquen bordes.
    Retorna (has_solid_bg, bg_color_hex, is_white_bg).
    """
    try:
        if isinstance(image_data_or_bytes, str):
            if 'base64,' in image_data_or_bytes:
                raw_b64 = image_data_or_bytes.split('base64,')[1]
            else:
                raw_b64 = image_data_or_bytes
            img_bytes = base64.b64decode(raw_b64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        elif isinstance(image_data_or_bytes, (bytes, bytearray)):
            img = Image.open(io.BytesIO(image_data_or_bytes)).convert("RGBA")
        else:
            img = Image.open(image_data_or_bytes).convert("RGBA")

        w, h = img.size
        rgba_arr = np.array(img)
        rgb_arr = rgba_arr[:, :, :3]
        alpha_arr = rgba_arr[:, :, 3]

        # Si el perímetro ya cuenta con transparencia (>25% con alpha < 30), el diseño ya viene aislado
        perimeter_alphas = np.concatenate([
            alpha_arr[0, :], alpha_arr[h - 1, :],
            alpha_arr[:, 0], alpha_arr[:, w - 1]
        ])
        if np.mean(perimeter_alphas < 30) > 0.25:
            return False, "#00000000", False

        # Muestrear franja perimetral de 2px
        strip_size = max(1, min(2, min(w, h) // 25))
        top_strip = rgb_arr[:strip_size, :, :].reshape(-1, 3)
        bottom_strip = rgb_arr[-strip_size:, :, :].reshape(-1, 3)
        left_strip = rgb_arr[:, :strip_size, :].reshape(-1, 3)
        right_strip = rgb_arr[:, -strip_size:, :].reshape(-1, 3)
        perimeter_colors = np.concatenate([top_strip, bottom_strip, left_strip, right_strip], axis=0)

        median_col = np.median(perimeter_colors, axis=0)
        r_med, g_med, b_med = int(median_col[0]), int(median_col[1]), int(median_col[2])

        # Distancia euclidiana de los pixeles perimetrales a la mediana
        dists = np.linalg.norm(perimeter_colors.astype(float) - median_col.astype(float), axis=1)

        # Fracción de pixeles perimetrales consistentes con el color de fondo
        solid_fraction = float(np.mean(dists < 45.0))

        has_solid_bg = bool(solid_fraction >= 0.50)
        bg_hex = f"#{r_med:02x}{g_med:02x}{b_med:02x}"
        is_white_bg = bool(r_med > 215 and g_med > 215 and b_med > 215)

        return has_solid_bg, bg_hex, is_white_bg
    except Exception:
        return False, "#ffffff", False


def apply_artistic_edit(image_data_or_bytes, edit_prompt):
    """
    Aplica ediciones artísticas al diseño textil subido:
    - Retiro de fondo / transparencia con antialiasing
    - Ajustes de saturación, contraste, brillo
    - Efectos vintage, sepia, blanco y negro, neón
    Retorna la data URL en base64 de la imagen procesada con transparencia.
    """
    if isinstance(image_data_or_bytes, str):
        if 'base64,' in image_data_or_bytes:
            raw_b64 = image_data_or_bytes.split('base64,')[1]
        else:
            raw_b64 = image_data_or_bytes
        img_bytes = base64.b64decode(raw_b64)
        input_data = io.BytesIO(img_bytes)
    elif isinstance(image_data_or_bytes, (bytes, bytearray)):
        input_data = io.BytesIO(image_data_or_bytes)
    else:
        input_data = image_data_or_bytes

    prompt_lower = edit_prompt.lower()

    shape_key, _ = detect_shape_request(prompt_lower)

    # 1. Si el usuario pide una forma o figura geométrica, aplicar el recorte primero
    if shape_key:
        shaped_url = apply_shape_mask(input_data, shape_key)
        raw_clean_b64 = shaped_url.split('base64,')[1]
        img = Image.open(io.BytesIO(base64.b64decode(raw_clean_b64))).convert("RGBA")
    else:
        # 1. Asegurar fondo aislado limpio
        cleaned_data_url = extract_and_clean_stamp(input_data, tolerance=38, auto_crop=True)
        raw_clean_b64 = cleaned_data_url.split('base64,')[1]
        img = Image.open(io.BytesIO(base64.b64decode(raw_clean_b64))).convert("RGBA")

    # Separar canal alfa
    r, g, b, a = img.split()
    rgb_img = Image.merge("RGB", (r, g, b))

    if any(k in prompt_lower for k in ['vintage', 'retro', 'sepia', 'antiguo', 'desgastado']):
        gray = ImageOps.grayscale(rgb_img)
        sepia = ImageOps.colorize(gray, "#2e1c0c", "#f4ecd8")
        rgb_img = Image.blend(rgb_img, sepia, 0.65)
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.15)

    elif any(k in prompt_lower for k in ['blanco y negro', 'monocromático', 'escala de grises', 'gris', 'b&w']):
        gray = ImageOps.grayscale(rgb_img)
        gray = ImageEnhance.Contrast(gray).enhance(1.35)
        rgb_img = gray.convert("RGB")

    elif any(k in prompt_lower for k in ['neón', 'neon', 'vibrante', 'saturar', 'más color', 'vivos', 'vivo', 'intensos']):
        rgb_img = ImageEnhance.Color(rgb_img).enhance(1.55)
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.2)

    elif any(k in prompt_lower for k in ['brillo', 'claro', 'iluminar', 'más claro']):
        rgb_img = ImageEnhance.Brightness(rgb_img).enhance(1.25)

    elif any(k in prompt_lower for k in ['invertir', 'inverso', 'negativo']):
        rgb_img = ImageOps.invert(rgb_img)

    else:
        # Mejora estándar de contraste y realce para estampado DTF
        rgb_img = ImageEnhance.Color(rgb_img).enhance(1.12)
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.08)

    r2, g2, b2 = rgb_img.split()
    final_img = Image.merge("RGBA", (r2, g2, b2, a))

    output_buffer = io.BytesIO()
    final_img.save(output_buffer, format="PNG", optimize=True)
    b64_str = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"


def detect_shape_request(prompt_text):
    """
    Detecta si el usuario está solicitando recortar o enmarcar la imagen en una forma geométrica:
    círculo/redonda, triángulo, rectángulo/cuadrado con esquinas redondeadas, hexágono, corazón, estrella, rombo.
    Retorna (shape_key, shape_label) o (None, None).
    """
    if not prompt_text:
        return None, None
    p = prompt_text.lower().strip()

    if any(k in p for k in ['redond', 'circul', 'círcul', 'óval', 'oval', 'esfer']):
        return 'circle', 'Circular'
    elif any(k in p for k in ['triang', 'triáng']):
        return 'triangle', 'Triangular'
    elif any(k in p for k in ['rectang', 'rectáng', 'cuadrad', 'esquinas redondead', 'borde redondead', 'tarjeta']):
        return 'rounded_rect', 'Rectangular Redondeado'
    elif any(k in p for k in ['hexag', 'hexág']):
        return 'hexagon', 'Hexagonal'
    elif any(k in p for k in ['coraz', 'coráz', 'heart']):
        return 'heart', 'Corazón'
    elif any(k in p for k in ['estrell', 'star']):
        return 'star', 'Estrella'
    elif any(k in p for k in ['romb', 'diamond']):
        return 'diamond', 'Rombo'

    return None, None


def apply_shape_mask(image_data_or_bytes, shape_type='circle'):
    """
    Recorta y enmascara la imagen a una figura geométrica con bordes suaves antialiasing:
    - 'circle': Círculo u óvalo perfecto
    - 'triangle': Triángulo simétrico
    - 'rounded_rect': Rectángulo con esquinas redondeadas
    - 'hexagon': Hexágono simétrico
    - 'heart': Corazón de autor
    - 'star': Estrella de 5 puntas
    - 'diamond': Rombo geométrico
    Devuelve un PNG transparente en formato data URL base64.
    """
    if isinstance(image_data_or_bytes, str):
        if 'base64,' in image_data_or_bytes:
            raw_b64 = image_data_or_bytes.split('base64,')[1]
        else:
            raw_b64 = image_data_or_bytes
        img_bytes = base64.b64decode(raw_b64)
        input_data = io.BytesIO(img_bytes)
    elif isinstance(image_data_or_bytes, (bytes, bytearray)):
        input_data = io.BytesIO(image_data_or_bytes)
    else:
        input_data = image_data_or_bytes

    img = Image.open(input_data).convert("RGBA")

    # Limitar resolución a 1400px para procesamiento fluido
    max_dim = 1400
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    orig_w, orig_h = img.size
    s = (shape_type or 'circle').lower()

    # 4x Supersampling para trazado de curvas antialiasing perfectas
    scale = 4
    W = max(16, orig_w * scale)
    H = max(16, orig_h * scale)
    pad = max(1, min(4 * scale, int(min(W, H) * 0.05)))
    dim = max(2, min(W, H) - 2 * pad)
    cx, cy = W / 2, H / 2

    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)

    if any(k in s for k in ['circul', 'redond', 'circle']):
        # Círculo perfecto proporcional (1:1) centrado
        r = dim / 2
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

    elif any(k in s for k in ['triang']):
        # Triángulo equilátero / isósceles armónico centrado
        h_tri = dim * 0.95
        points = [
            (cx, cy - h_tri / 2),
            (cx + dim / 2, cy + h_tri / 2),
            (cx - dim / 2, cy + h_tri / 2)
        ]
        draw.polygon(points, fill=255)

    elif any(k in s for k in ['coraz', 'heart']):
        r = dim / 34.0
        cy_h = cy - (dim * 0.04)
        points = []
        for deg in range(0, 360, 2):
            t = math.radians(deg)
            x = cx + r * (16 * (math.sin(t) ** 3))
            y = cy_h - r * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            points.append((x, y))
        draw.polygon(points, fill=255)

    elif any(k in s for k in ['hexag']):
        R = dim / 2
        points = []
        for i in range(6):
            t = math.radians(i * 60 - 30)
            points.append((cx + R * math.cos(t), cy + R * math.sin(t)))
        draw.polygon(points, fill=255)

    elif any(k in s for k in ['estrell', 'star']):
        R = dim / 2
        inner_r = R * 0.42
        points = []
        for i in range(10):
            rad = R if i % 2 == 0 else inner_r
            t = math.radians(i * 36 - 90)
            points.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
        draw.polygon(points, fill=255)

    elif any(k in s for k in ['romb', 'diamond']):
        points = [
            (cx, cy - dim / 2),
            (cx + dim / 2, cy),
            (cx, cy + dim / 2),
            (cx - dim / 2, cy)
        ]
        draw.polygon(points, fill=255)

    elif any(k in s for k in ['rectang', 'cuadrad', 'esquina', 'rounded']):
        # Rectángulo o tarjeta con esquinas redondeadas
        radius = min(W, H) * 0.12
        draw.rounded_rectangle((pad, pad, W - pad, H - pad), radius=radius, fill=255)

    else:
        # Por defecto: Círculo perfecto proporcional
        r = dim / 2
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

    # Redimensionar la máscara al tamaño original con suavizado LANCZOS
    mask_smooth = mask.resize((orig_w, orig_h), Image.Resampling.LANCZOS)

    r_ch, g_ch, b_ch, a_ch = img.split()
    final_a = ImageChops.multiply(a_ch, mask_smooth)
    shaped_img = Image.merge("RGBA", (r_ch, g_ch, b_ch, final_a))

    # Auto-recortar los márgenes vacíos transparentes
    bbox = shaped_img.getbbox()
    if bbox:
        # Pequeño padding de 2px para no cortar contornos
        x0 = max(0, bbox[0] - 2)
        y0 = max(0, bbox[1] - 2)
        x1 = min(orig_w, bbox[2] + 2)
        y1 = min(orig_h, bbox[3] + 2)
        shaped_img = shaped_img.crop((x0, y0, x1, y1))

    # Realce sutil de contraste para DTF
    shaped_img = ImageEnhance.Contrast(shaped_img).enhance(1.04)

    output_buffer = io.BytesIO()
    shaped_img.save(output_buffer, format="PNG", optimize=True)
    b64_str = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"


