# 👕 StampCol — Plataforma Web de Personalización de Buzos & Hoodies con IA

Plataforma web profesional para **StampCol**, desarrollada con **Django (Python)**, **Tailwind CSS (Mobile-First)**, **HTML5 Canvas API** e integración con **Google Gemini AI** y pedidos directos a **WhatsApp**.

---

## 🚀 Características Principales

- **Arquitectura MVT (Modelo-Vista-Template):** Código limpio, desacoplado y modular.
- **Canvas Interactivo HTML5:**
  - Alternador de vista **Frente** y **Espalda**.
  - Cambio dinámico de color del buzo en tiempo real con sombras y pliegues realistas.
  - Soporte táctil en dispositivos móviles (arrastrar, escalar con dos dedos y rotar).
  - Carga de imágenes personalizadas por el usuario o selección de stickers prediseñados.
  - Exportación automática del mockup fusionado en formato PNG de alta resolución.
- **Asesor Creativo con Google Gemini AI:**
  - Drawer / Chat flotante optimizado para móviles.
  - Sugerencias inteligentes de estilo (Cyberpunk, Anime, Retro, Frases, Streetwear).
  - Recomendación y aplicación directa de paletas de color al buzo con 1 clic.
- **Checkout Optimizado para WhatsApp:**
  - Botón Sticky ("Sticky Bottom CTA") en móviles.
  - Almacena el pedido en la base de datos SQLite/PostgreSQL con las imágenes de diseño.
  - Descarga el mockup al dispositivo del cliente y lo redirige a WhatsApp con el mensaje pre-llenado.

---

## 📂 Estructura del Proyecto

```text
StampCol/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── stampcol_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── customizer/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   ├── static/customizer/
│   │   ├── images/
│   │   │   ├── hoodie_front.svg
│   │   │   ├── hoodie_back.svg
│   │   │   └── samples/
│   │   └── js/
│   │       ├── canvas_editor.js
│   │       └── gemini_chat.js
│   └── templates/customizer/
│       └── index.html
└── media/
    └── orders/
```

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Clonar o acceder al directorio del proyecto
```bash
cd c:\laragon\www\StampCol
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia `.env.example` a `.env` y añade tu clave de Gemini:
```env
GEMINI_API_KEY=tu_clave_de_google_ai_studio
WHATSAPP_NUMBER=573001234567
```
*(Nota: Si no agregas la clave de Gemini de inmediato, la plataforma incluye respuestas creativas simuladas sin romper el flujo de la aplicación).*

### 4. Ejecutar migraciones y cargar catálogo inicial
```bash
python manage.py makemigrations customizer
python manage.py migrate
python manage.py seed_data
```

### 5. Crear superusuario para el panel de administración
```bash
python manage.py createsuperuser
```

### 6. Iniciar el servidor local
```bash
python manage.py runserver
```

Abre tu navegador en `http://127.0.0.1:8000/`.

---

## 🧪 Pruebas Automatizadas
Ejecuta la suite de pruebas unitarias:
```bash
python manage.py test
```
