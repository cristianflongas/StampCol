/**
 * StampCol - Real Photo T-Shirt Canvas Editor Engine (Photorealistic Studio v4)
 * Motor de personalización fotorrealista para Camisetas StampCol.
 * Renderiza la fotografía real de la prenda con conservación de sombras,
 * textura textil de algodón peinado (creases, pliegues, ribetes) en TODOS los colores
 * (incluyendo Negro carbón y Blanco puro) y gestiona estampados DTF en Frente y Espalda.
 */

class HoodieCustomizer {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });

        // Proporción fotorrealista de la prenda (600x813)
        this.baseWidth = 600;
        this.baseHeight = 813;
        this.canvas.width = this.baseWidth;
        this.canvas.height = this.baseHeight;

        this.currentView = 'front'; // 'front' | 'back'
        this.currentColor = options.initialColor || '#FFFFFF';
        this.currentColorName = options.initialColorName || 'Blanco';

        // Capas independientes de diseño (Frente y Espalda)
        this.layers = {
            front: {
                hasDesign: false,
                sourceUrl: null, // Si provino de Pinterest u otra URL
                img: null,
                imgSrc: null,
                rawOriginalSrc: null,
                rawOriginalImage: null,
                isolatedSrc: null,
                isolatedImage: null,
                isBackgroundRemoved: false,
                appliedShape: null,
                x: 300,
                y: 370,
                scale: 0.85,
                rotation: 0,
                width: 240,
                height: 240,
            },
            back: {
                hasDesign: false,
                sourceUrl: null, // Si provino de Pinterest u otra URL
                img: null,
                imgSrc: null,
                rawOriginalSrc: null,
                rawOriginalImage: null,
                isolatedSrc: null,
                isolatedImage: null,
                isBackgroundRemoved: false,
                appliedShape: null,
                x: 300,
                y: 390,
                scale: 0.95,
                rotation: 0,
                width: 260,
                height: 260,
            }
        };

        // URLs de las imágenes de alta definición de la camiseta y logo de marca
        this.frontImgUrl = options.frontImgUrl || '/static/customizer/images/tshirt_real_front.png';
        this.backImgUrl = options.backImgUrl || '/static/customizer/images/tshirt_real_back.png';
        this.logoUrl = options.logoUrl || '/static/customizer/images/logo_stampcol.png';

        this.images = {
            front: new Image(),
            back: new Image()
        };

        this.logoImg = new Image();
        this.logoImg.crossOrigin = 'anonymous';
        this.logoImg.src = this.logoUrl;

        // Almacenamiento de imagen sin procesar (datos de píxeles originales para recálculo ultra-rápido)
        this.rawImageData = {
            front: null,
            back: null
        };

        // Canvases tintados en caché
        this.tintedCanvas = {
            front: document.createElement('canvas'),
            back: document.createElement('canvas')
        };
        this.tintedCanvas.front.width = this.baseWidth;
        this.tintedCanvas.front.height = this.baseHeight;
        this.tintedCanvas.back.width = this.baseWidth;
        this.tintedCanvas.back.height = this.baseHeight;

        // Canvas auxiliar para recorte/enmascarado a la silueta de la camiseta
        this.stampCanvas = document.createElement('canvas');
        this.stampCanvas.width = this.baseWidth;
        this.stampCanvas.height = this.baseHeight;
        this.stampCtx = this.stampCanvas.getContext('2d');

        // Control de interacción y gestos
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.layerStartX = 0;
        this.layerStartY = 0;
        this.initialPinchDistance = null;
        this.initialPinchScale = 1;

        this.init();
    }

    async init() {
        await this.loadBaseImages();
        this.extractRawData();
        this.updateTintedCanvases();
        this.bindEvents();
        this.render();
    }

    loadBaseImages() {
        return new Promise((resolve) => {
            let loaded = 0;
            const check = () => {
                loaded++;
                if (loaded >= 2) resolve();
            };

            this.images.front.crossOrigin = 'anonymous';
            this.images.back.crossOrigin = 'anonymous';

            this.images.front.onload = check;
            this.images.back.onload = check;

            this.images.front.src = this.frontImgUrl;
            this.images.back.src = this.backImgUrl;
        });
    }

    extractRawData() {
        ['front', 'back'].forEach(view => {
            const img = this.images[view];
            if (!img.complete || img.naturalWidth === 0) return;
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.baseWidth;
            tempCanvas.height = this.baseHeight;
            const tempCtx = tempCanvas.getContext('2d', { willReadFrequently: true });
            tempCtx.drawImage(img, 0, 0, this.baseWidth, this.baseHeight);
            this.rawImageData[view] = tempCtx.getImageData(0, 0, this.baseWidth, this.baseHeight);
        });
    }

    /**
     * Motor de tintado fotorrealista:
     * Calcula píxel a píxel la interacción entre la luz sobre la tela de algodón,
     * las sombras en pliegues y el color seleccionado.
     */
    updateTintedCanvases() {
        const hex = this.currentColor.replace('#', '');
        let tr = 255, tg = 255, tb = 255;
        if (hex.length === 6) {
            tr = parseInt(hex.substring(0, 2), 16);
            tg = parseInt(hex.substring(2, 4), 16);
            tb = parseInt(hex.substring(4, 6), 16);
        } else if (hex.length === 3) {
            tr = parseInt(hex[0] + hex[0], 16);
            tg = parseInt(hex[1] + hex[1], 16);
            tb = parseInt(hex[2] + hex[2], 16);
        }

        const targetLum = (tr * 0.299 + tg * 0.587 + tb * 0.114) / 255.0;

        ['front', 'back'].forEach(view => {
            const rawData = this.rawImageData[view];
            const tCanvas = this.tintedCanvas[view];
            const tCtx = tCanvas.getContext('2d');

            if (!rawData) {
                // Fallback rápido si los datos crudos aún no cargaron
                const rawImg = this.images[view];
                if (rawImg && rawImg.complete) {
                    tCtx.clearRect(0, 0, this.baseWidth, this.baseHeight);
                    tCtx.drawImage(rawImg, 0, 0, this.baseWidth, this.baseHeight);
                }
                return;
            }

            const src = rawData.data;
            const outImgData = tCtx.createImageData(this.baseWidth, this.baseHeight);
            const dst = outImgData.data;
            const len = src.length;

            const isNeutral = (Math.max(tr, tg, tb) - Math.min(tr, tg, tb)) < 24;
            const isWhite = isNeutral && (targetLum > 0.94);
            const isBlack = isNeutral && (targetLum < 0.22);
            const L_base = 0.88; // Referencia de luz difusa en tela de algodón

            for (let i = 0; i < len; i += 4) {
                const a = src[i + 3];
                if (a === 0) {
                    dst[i + 3] = 0;
                    continue;
                }

                const r = src[i];
                const g = src[i + 1];
                const b = src[i + 2];
                const lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0;

                if (isWhite) {
                    // Camiseta Blanca: conservación fiel de sombras naturales de algodón
                    dst[i]     = r;
                    dst[i + 1] = g;
                    dst[i + 2] = b;
                } else if (isBlack) {
                    // Camiseta Negra / Carbón Streetwear: Negro profundo auténtico (#121212)
                    // Pliegues y costuras hiperrealistas sin deslavar a gris ceniza
                    const factor = Math.pow(lum, 2.5);
                    const baseDarkR = Math.max(4, Math.round(tr * 0.45));
                    const baseDarkG = Math.max(4, Math.round(tg * 0.45));
                    const baseDarkB = Math.max(4, Math.round(tb * 0.45));
                    const lift = Math.max(10, Math.round(tr * 0.65));

                    dst[i]     = Math.min(255, Math.max(baseDarkR, Math.round(baseDarkR + factor * lift)));
                    dst[i + 1] = Math.min(255, Math.max(baseDarkG, Math.round(baseDarkG + factor * lift)));
                    dst[i + 2] = Math.min(255, Math.max(baseDarkB, Math.round(baseDarkB + factor * lift)));
                } else {
                    // Colores textiles auténticos (Amarillo, Rojo, Azul, etc.)
                    // Conserva el tinte real, resalta pliegues, sombras y costuras sin quemar en fosforescente
                    if (lum <= L_base) {
                        const ratio = Math.pow(lum / L_base, 1.25);
                        dst[i]     = Math.min(255, Math.max(0, Math.round(tr * ratio)));
                        dst[i + 1] = Math.min(255, Math.max(0, Math.round(tg * ratio)));
                        dst[i + 2] = Math.min(255, Math.max(0, Math.round(tb * ratio)));
                    } else {
                        const hRatio = (lum - L_base) / (1.0 - L_base + 0.0001);
                        dst[i]     = Math.min(255, Math.max(0, Math.round(tr + (255 - tr) * hRatio * 0.38)));
                        dst[i + 1] = Math.min(255, Math.max(0, Math.round(tg + (255 - tg) * hRatio * 0.38)));
                        dst[i + 2] = Math.min(255, Math.max(0, Math.round(tb + (255 - tb) * hRatio * 0.38)));
                    }
                }
                dst[i + 3] = a;
            }

            tCtx.putImageData(outImgData, 0, 0);
        });
    }

    setColor(hexCode, colorName) {
        this.currentColor = hexCode;
        if (colorName) this.currentColorName = colorName;
        this.updateTintedCanvases();
        this.render();
    }

    setView(viewName) {
        if (viewName !== 'front' && viewName !== 'back') return;
        this.currentView = viewName;
        this.render();
        this.triggerViewChangeUI(viewName);
    }

    getCurrentLayer() {
        return this.layers[this.currentView];
    }

    setDesignFromUrl(url, targetView = null, options = {}) {
        if (!url) return;
        const viewToUse = targetView || this.currentView;
        if (targetView && this.currentView !== targetView) {
            this.setView(targetView);
        }

        const layer = this.layers[viewToUse];
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            layer.img = img;
            layer.imgSrc = url;
            layer.hasDesign = true;
            if (options.sourceUrl) {
                layer.sourceUrl = options.sourceUrl;
            }

            // Preservar la imagen original y sincronizar estado de fondo
            if (!options.preserveHistory) {
                if (!layer.rawOriginalSrc || options.overrideRaw) {
                    layer.rawOriginalSrc = url;
                    layer.rawOriginalImage = img;
                }
                if (options.isIsolated) {
                    layer.isolatedSrc = url;
                    layer.isolatedImage = img;
                    layer.isBackgroundRemoved = true;
                } else if (!layer.isolatedSrc) {
                    layer.isBackgroundRemoved = false;
                }
                if (options.shape) {
                    layer.appliedShape = options.shape;
                }
            }
            if (options.isIsolated) {
                layer.isolatedSrc = url;
                layer.isolatedImage = img;
                layer.isBackgroundRemoved = true;
            }

            // Dimensionamiento armónico para el pecho o espalda
            if (!options.preserveTransform) {
                const maxDim = Math.max(img.naturalWidth || 280, img.naturalHeight || 280);
                const targetBaseDim = (viewToUse === 'front') ? 260 : 310;
                const normFactor = maxDim > 0 ? (targetBaseDim / maxDim) : 1;

                layer.width = (img.naturalWidth || 280) * normFactor;
                layer.height = (img.naturalHeight || 280) * normFactor;

                if (viewToUse === 'front') {
                    layer.x = 300;
                    layer.y = 370;
                    layer.scale = 1.0;
                } else {
                    layer.x = 300;
                    layer.y = 390;
                    layer.scale = 1.0;
                }
                layer.rotation = 0;
            }

            this.syncControlsUI();
            this.render();

            try {
                window.dispatchEvent(new CustomEvent('stampcol:design-changed', {
                    detail: { url: url, view: viewToUse }
                }));
            } catch (e) {}
        };
        img.src = url;
    }

    /**
     * Adapta y recorta el estampado activo a figuras geométricas:
     * 'circle', 'triangle', 'rounded_rect', 'hexagon', 'heart', 'star', 'diamond', 'original'.
     */
    async applyShape(shapeType) {
        const layer = this.getCurrentLayer();
        if (!layer || !layer.hasDesign || !layer.imgSrc) return null;

        if (!layer.rawOriginalSrc) {
            layer.rawOriginalSrc = layer.imgSrc;
        }
        if (!layer.rawOriginalImage && layer.img) {
            layer.rawOriginalImage = layer.img;
        }

        const s = (shapeType || '').toLowerCase().trim();

        // 1. Si se solicita la versión original / restablecer
        if (!s || s === 'original' || s === 'none' || s === 'reset' || s === 'restablecer') {
            layer.appliedShape = null;
            const currentX = layer.x;
            const currentY = layer.y;
            const currentScale = layer.scale;
            const currentRot = layer.rotation;
            const targetUrl = (layer.isBackgroundRemoved && layer.isolatedSrc) ? layer.isolatedSrc : layer.rawOriginalSrc;

            return new Promise((resolve) => {
                this.setDesignFromUrl(targetUrl, this.currentView, {
                    preserveHistory: true,
                    preserveTransform: true
                });
                setTimeout(() => {
                    layer.x = currentX;
                    layer.y = currentY;
                    layer.scale = currentScale;
                    layer.rotation = currentRot;
                    this.syncControlsUI();
                    this.render();
                    resolve(targetUrl);
                }, 80);
            });
        }

        layer.appliedShape = s;

        // Base URL a recortar (si el usuario ya había quitado fondo, mantener transparencia)
        const baseSrc = (layer.isBackgroundRemoved && layer.isolatedSrc) ? layer.isolatedSrc : (layer.rawOriginalSrc || layer.imgSrc);

        const applyResultToLayer = (dataUrl) => {
            return new Promise((resolve) => {
                const currentX = layer.x;
                const currentY = layer.y;
                const currentScale = layer.scale;
                const currentRot = layer.rotation;

                const shapedImg = new Image();
                shapedImg.crossOrigin = 'anonymous';
                shapedImg.onload = () => {
                    layer.img = shapedImg;
                    layer.imgSrc = dataUrl;
                    layer.appliedShape = s;
                    layer.x = currentX;
                    layer.y = currentY;
                    layer.scale = currentScale;
                    layer.rotation = currentRot;
                    this.syncControlsUI();
                    this.render();
                    try {
                        window.dispatchEvent(new CustomEvent('stampcol:design-changed', {
                            detail: { url: dataUrl, view: this.currentView }
                        }));
                    } catch (e) {}
                    resolve(dataUrl);
                };
                shapedImg.onerror = () => {
                    resolve(null);
                };
                shapedImg.src = dataUrl;
            });
        };

        // 2. Intento de recorte rápido local mediante Canvas
        try {
            let srcImg = null;
            if (layer.isBackgroundRemoved && layer.isolatedImage && layer.isolatedImage.complete && layer.isolatedImage.naturalWidth > 0) {
                srcImg = layer.isolatedImage;
            } else if (!layer.isBackgroundRemoved && layer.rawOriginalImage && layer.rawOriginalImage.complete && layer.rawOriginalImage.naturalWidth > 0) {
                srcImg = layer.rawOriginalImage;
            } else {
                srcImg = layer.img;
            }

            if (!srcImg || !srcImg.complete || (srcImg.naturalWidth <= 0 && srcImg.width <= 0)) {
                throw new Error("Imagen fuente no cargada aún en canvas local.");
            }

            const origW = srcImg.naturalWidth || srcImg.width || 400;
            const origH = srcImg.naturalHeight || srcImg.height || 400;

            const isRoundedRect = s.includes('round') || s.includes('redondead');
            const isCircle = !isRoundedRect && (s.includes('circle') || s.includes('circul'));
            const isTriangle = s.includes('triang');
            const isHeart = s.includes('heart') || s.includes('coraz');
            const isHexagon = s.includes('hexag');
            const isStar = s.includes('star') || s.includes('estrell');
            const isDiamond = s.includes('romb') || s.includes('diamond');
            const isSquare1x1 = isCircle || isTriangle || isHeart || isHexagon || isStar || isDiamond;

            const offCanvas = document.createElement('canvas');
            const offCtx = offCanvas.getContext('2d');

            const dim = Math.min(origW, origH);
            let targetW = origW;
            let targetH = origH;
            let cropX = 0;
            let cropY = 0;

            if (isSquare1x1) {
                targetW = dim;
                targetH = dim;
                cropX = (origW - dim) / 2;
                cropY = (origH - dim) / 2;
            }

            offCanvas.width = targetW;
            offCanvas.height = targetH;

            offCtx.save();
            offCtx.beginPath();

            const W = targetW;
            const H = targetH;
            const cx = W / 2;
            const cy = H / 2;
            const pad = 2;
            const D = Math.min(W, H) - pad * 2;

            if (isCircle) {
                offCtx.arc(cx, cy, D / 2, 0, Math.PI * 2);
            } else if (isTriangle) {
                const hTri = D * 0.95;
                offCtx.moveTo(cx, cy - hTri / 2);
                offCtx.lineTo(cx + D / 2, cy + hTri / 2);
                offCtx.lineTo(cx - D / 2, cy + hTri / 2);
                offCtx.closePath();
            } else if (isHeart) {
                const r = D / 34;
                const cyH = cy - (D * 0.04);
                for (let deg = 0; deg < 360; deg += 2) {
                    const t = (deg * Math.PI) / 180;
                    const x = cx + r * (16 * Math.pow(Math.sin(t), 3));
                    const y = cyH - r * (13 * Math.cos(t) - 5 * Math.cos(2*t) - 2 * Math.cos(3*t) - Math.cos(4*t));
                    if (deg === 0) offCtx.moveTo(x, y);
                    else offCtx.lineTo(x, y);
                }
                offCtx.closePath();
            } else if (isHexagon) {
                const R = D / 2;
                for (let i = 0; i < 6; i++) {
                    const t = ((i * 60 - 30) * Math.PI) / 180;
                    const x = cx + R * Math.cos(t);
                    const y = cy + R * Math.sin(t);
                    if (i === 0) offCtx.moveTo(x, y);
                    else offCtx.lineTo(x, y);
                }
                offCtx.closePath();
            } else if (isStar) {
                const R = D / 2;
                const innerR = R * 0.42;
                for (let i = 0; i < 10; i++) {
                    const rad = (i % 2 === 0) ? R : innerR;
                    const t = ((i * 36 - 90) * Math.PI) / 180;
                    const x = cx + rad * Math.cos(t);
                    const y = cy + rad * Math.sin(t);
                    if (i === 0) offCtx.moveTo(x, y);
                    else offCtx.lineTo(x, y);
                }
                offCtx.closePath();
            } else if (isDiamond) {
                offCtx.moveTo(cx, cy - D / 2);
                offCtx.lineTo(cx + D / 2, cy);
                offCtx.lineTo(cx, cy + D / 2);
                offCtx.lineTo(cx - D / 2, cy);
                offCtx.closePath();
            } else if (isRoundedRect) {
                const radius = Math.min(W, H) * 0.12;
                if (offCtx.roundRect) {
                    offCtx.roundRect(pad, pad, W - pad * 2, H - pad * 2, radius);
                } else {
                    offCtx.rect(pad, pad, W - pad * 2, H - pad * 2);
                }
            } else {
                offCtx.rect(pad, pad, W - pad * 2, H - pad * 2);
            }

            offCtx.clip();

            if (isSquare1x1) {
                offCtx.drawImage(srcImg, cropX, cropY, dim, dim, 0, 0, targetW, targetH);
            } else {
                offCtx.drawImage(srcImg, 0, 0, targetW, targetH);
            }

            offCtx.restore();

            const shapedDataUrl = offCanvas.toDataURL('image/png');
            return await applyResultToLayer(shapedDataUrl);
        } catch (clientErr) {
            console.warn('Recorte en cliente no completado, activando motor del servidor:', clientErr);
        }

        // 3. Fallback infalible de alta precisión en Servidor (Python PIL con antialiasing)
        try {
            function getCsrf() {
                const match = document.cookie.match(/csrftoken=([^;]+)/);
                return match ? match[1] : '';
            }
            const res = await fetch('/api/isolate-stamp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf()
                },
                body: JSON.stringify({
                    image_base64: baseSrc,
                    shape: s,
                    remove_bg: Boolean(layer.isBackgroundRemoved)
                })
            });
            const data = await res.json();
            const serverResult = data.isolated_image || data.isolated_stamp_base64;
            if (data.status === 'success' && serverResult) {
                return await applyResultToLayer(serverResult);
            }
        } catch (serverErr) {
            console.error('Error aplicando forma en servidor:', serverErr);
        }

        return null;
    }

    getCurrentDesignUrl() {
        const layer = this.getCurrentLayer();
        return (layer && layer.hasDesign) ? layer.imgSrc : null;
    }

    setDesignFromFile(file) {
        if (!file || !file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            this.setDesignFromUrl(e.target.result);
        };
        reader.readAsDataURL(file);
    }

    removeCurrentDesign() {
        const layer = this.getCurrentLayer();
        layer.hasDesign = false;
        layer.img = null;
        layer.imgSrc = null;
        layer.rawOriginalSrc = null;
        layer.rawOriginalImage = null;
        layer.isolatedSrc = null;
        layer.isolatedImage = null;
        layer.isBackgroundRemoved = false;
        layer.appliedShape = null;
        layer.sourceUrl = null;
        this.syncControlsUI();
        this.render();

        try {
            window.dispatchEvent(new CustomEvent('stampcol:design-removed', {
                detail: { view: this.currentView }
            }));
        } catch (e) {}
    }

    removeAllDesigns() {
        ['front', 'back'].forEach(view => {
            const layer = this.layers[view];
            if (layer) {
                layer.hasDesign = false;
                layer.img = null;
                layer.imgSrc = null;
                layer.rawOriginalSrc = null;
                layer.rawOriginalImage = null;
                layer.isolatedSrc = null;
                layer.isolatedImage = null;
                layer.isBackgroundRemoved = false;
                layer.appliedShape = null;
                layer.sourceUrl = null;
            }
        });
        this.syncControlsUI();
        this.render();

        try {
            window.dispatchEvent(new CustomEvent('stampcol:design-removed', {
                detail: { view: 'all' }
            }));
        } catch (e) {}
    }

    centerDesign() {
        const layer = this.getCurrentLayer();
        if (!layer.hasDesign) return;
        layer.x = 300;
        layer.y = (this.currentView === 'front') ? 370 : 390;
        layer.rotation = 0;
        this.syncControlsUI();
        this.render();
    }

    setDesignScale(scaleValue) {
        const layer = this.getCurrentLayer();
        if (!layer.hasDesign) return;
        layer.scale = Math.max(0.1, Math.min(4.0, parseFloat(scaleValue)));

        const scaleRange = document.getElementById('design-scale-slider');
        if (scaleRange && Math.abs(parseFloat(scaleRange.value) - layer.scale) > 0.005) {
            scaleRange.value = layer.scale;
        }
        const scaleDisplay = document.getElementById('scale-value-display');
        if (scaleDisplay) {
            scaleDisplay.textContent = `${Math.round(layer.scale * 100)}%`;
        }
        this.render();
    }

    setDesignRotation(degrees) {
        const layer = this.getCurrentLayer();
        if (!layer.hasDesign) return;
        layer.rotation = parseFloat(degrees);
        this.render();
    }

    /**
     * Dibuja el estampado DTF recortado estrictamente a la silueta de la camiseta.
     * Añade un acabado sutil de termofijado textil para máxima naturalidad.
     */
    renderMaskedStamp(targetCtx, view, drawDashedBox = false) {
        const layer = this.layers[view];
        if (!layer || !layer.hasDesign || !layer.img || !layer.img.complete) return;

        const rawImg = this.images[view];
        const sCtx = this.stampCtx;
        sCtx.clearRect(0, 0, this.baseWidth, this.baseHeight);

        // 1. Dibujar el diseño en el canvas auxiliar
        sCtx.save();
        sCtx.translate(layer.x, layer.y);
        sCtx.rotate((layer.rotation * Math.PI) / 180);

        const drawW = layer.width * layer.scale;
        const drawH = layer.height * layer.scale;
        sCtx.drawImage(layer.img, -drawW / 2, -drawH / 2, drawW, drawH);
        sCtx.restore();

        // 2. Máscara estricta a la silueta de la camiseta
        if (rawImg && rawImg.complete && rawImg.naturalWidth > 0) {
            sCtx.save();
            sCtx.globalCompositeOperation = 'destination-in';
            sCtx.drawImage(rawImg, 0, 0, this.baseWidth, this.baseHeight);
            sCtx.restore();
        }

        // 3. Estampar sobre el lienzo principal con acabado DTF Ultra HD
        targetCtx.save();
        targetCtx.drawImage(this.stampCanvas, 0, 0, this.baseWidth, this.baseHeight);
        targetCtx.restore();

        // 4. Guía visual punteada elegante mientras el usuario interactúa
        if (drawDashedBox) {
            targetCtx.save();
            targetCtx.translate(layer.x, layer.y);
            targetCtx.rotate((layer.rotation * Math.PI) / 180);
            targetCtx.strokeStyle = 'rgba(245, 158, 11, 0.9)'; // Ámbar StampCol
            targetCtx.lineWidth = 1.5;
            targetCtx.setLineDash([5, 5]);
            targetCtx.strokeRect(-drawW / 2 - 4, -drawH / 2 - 4, drawW + 8, drawH + 8);
            targetCtx.restore();
        }
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.baseWidth, this.baseHeight);

        // 1. Sombra de piso / levitación elíptica 3D proyectada en el suelo del estudio
        const shadowY = 746;
        const groundGrad = ctx.createRadialGradient(
            this.baseWidth / 2, shadowY, 0,
            this.baseWidth / 2, shadowY, 210
        );
        groundGrad.addColorStop(0, 'rgba(15, 23, 42, 0.36)');
        groundGrad.addColorStop(0.35, 'rgba(15, 23, 42, 0.18)');
        groundGrad.addColorStop(0.70, 'rgba(15, 23, 42, 0.05)');
        groundGrad.addColorStop(1, 'rgba(15, 23, 42, 0)');

        ctx.save();
        ctx.fillStyle = groundGrad;
        ctx.beginPath();
        ctx.ellipse(this.baseWidth / 2, shadowY, 210, 18, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // 2. Prenda real con doble capa de sombra de levitación flotante en 3D
        const tCanvas = this.tintedCanvas[this.currentView];
        if (tCanvas) {
            // Capa A: Sombra de flotación profunda que despega la prenda del fondo
            ctx.save();
            ctx.shadowColor = 'rgba(15, 23, 42, 0.28)';
            ctx.shadowBlur = 38;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 22;
            ctx.drawImage(tCanvas, 0, 0, this.baseWidth, this.baseHeight);
            ctx.restore();

            // Capa B: Sombra de oclusión ambiental cercana
            ctx.save();
            ctx.shadowColor = 'rgba(15, 23, 42, 0.16)';
            ctx.shadowBlur = 12;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 6;
            ctx.drawImage(tCanvas, 0, 0, this.baseWidth, this.baseHeight);
            ctx.restore();

            // Capa C: Prenda nítida
            ctx.drawImage(tCanvas, 0, 0, this.baseWidth, this.baseHeight);
        }

        // 3. Estampado DTF con recorte anatómico
        this.renderMaskedStamp(ctx, this.currentView, this.isDragging);
    }

    getCanvasCoords(e) {
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const scaleX = this.baseWidth / rect.width;
        const scaleY = this.baseHeight / rect.height;
        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
        };
    }

    isPointInsideDesign(x, y) {
        const layer = this.getCurrentLayer();
        if (!layer.hasDesign) return false;
        const drawW = (layer.width * layer.scale) / 2 + 25;
        const drawH = (layer.height * layer.scale) / 2 + 25;
        return Math.abs(x - layer.x) <= drawW && Math.abs(y - layer.y) <= drawH;
    }

    bindEvents() {
        const onStart = (e) => {
            if (e.touches && e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                this.initialPinchDistance = Math.hypot(dx, dy);
                this.initialPinchScale = this.getCurrentLayer().scale;
                return;
            }

            const { x, y } = this.getCanvasCoords(e);
            if (this.isPointInsideDesign(x, y)) {
                this.isDragging = true;
                this.dragStartX = x;
                this.dragStartY = y;
                const layer = this.getCurrentLayer();
                this.layerStartX = layer.x;
                this.layerStartY = layer.y;
                this.canvas.classList.add('is-interacting');
                document.getElementById('canvas-ground-shadow')?.classList.add('is-interacting');
                this.render();
                if (e.cancelable) e.preventDefault();
            }
        };

        const onMove = (e) => {
            if (e.touches && e.touches.length === 2 && this.initialPinchDistance) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const currentDist = Math.hypot(dx, dy);
                const factor = currentDist / this.initialPinchDistance;
                this.setDesignScale(this.initialPinchScale * factor);
                this.syncControlsUI();
                if (e.cancelable) e.preventDefault();
                return;
            }

            if (!this.isDragging) {
                const { x, y } = this.getCanvasCoords(e);
                this.canvas.style.cursor = this.isPointInsideDesign(x, y) ? 'grab' : 'default';
                return;
            }

            this.canvas.style.cursor = 'grabbing';
            const { x, y } = this.getCanvasCoords(e);
            const deltaX = x - this.dragStartX;
            const deltaY = y - this.dragStartY;
            const layer = this.getCurrentLayer();

            layer.x = Math.max(-200, Math.min(800, this.layerStartX + deltaX));
            layer.y = Math.max(-150, Math.min(950, this.layerStartY + deltaY));

            this.render();
            if (e.cancelable) e.preventDefault();
        };

        const onEnd = () => {
            if (this.isDragging) {
                this.isDragging = false;
                this.initialPinchDistance = null;
                this.canvas.style.cursor = 'default';
                this.canvas.classList.remove('is-interacting');
                document.getElementById('canvas-ground-shadow')?.classList.remove('is-interacting');
                this.render();
            } else {
                this.initialPinchDistance = null;
            }
        };

        this.canvas.addEventListener('mousedown', onStart);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onEnd);

        this.canvas.addEventListener('touchstart', onStart, { passive: false });
        window.addEventListener('touchmove', onMove, { passive: false });
        window.addEventListener('touchend', onEnd);

        // Zoom rápido con la rueda del ratón al pasar el cursor sobre la prenda
        this.canvas.addEventListener('wheel', (e) => {
            const layer = this.getCurrentLayer();
            if (!layer || !layer.hasDesign) return;
            const { x, y } = this.getCanvasCoords(e);
            if (this.isPointInsideDesign(x, y)) {
                e.preventDefault();
                const step = e.deltaY < 0 ? 0.08 : -0.08;
                this.setDesignScale(layer.scale + step);
            }
        }, { passive: false });

        // Atajo de teclado: Eliminar diseño con la tecla Supr (Delete) o Retroceso (Backspace)
        window.addEventListener('keydown', (e) => {
            const target = e.target;
            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
                return;
            }
            if (e.key === 'Delete' || e.key === 'Backspace') {
                const layer = this.getCurrentLayer();
                if (layer && layer.hasDesign) {
                    e.preventDefault();
                    if (typeof window.removeActiveDesign === 'function') {
                        window.removeActiveDesign();
                    } else {
                        this.removeCurrentDesign();
                    }
                }
            }
        });
    }

    getSnapshotBase64(view, addBrandWatermark = false, transparentBg = false) {
        const originalView = this.currentView;
        this.currentView = view;

        // Canvas fuera de pantalla para generar la camiseta flotante en alta resolución
        const offCanvas = document.createElement('canvas');
        offCanvas.width = this.baseWidth;
        offCanvas.height = this.baseHeight;
        const ctx = offCanvas.getContext('2d');

        const tCanvas = this.tintedCanvas[this.currentView];

        if (transparentBg) {
            // Modo transparente puro (para recortar o componer en la Hoja de Confección)
            if (tCanvas) {
                ctx.drawImage(tCanvas, 0, 0, this.baseWidth, this.baseHeight);
            }
            this.renderMaskedStamp(ctx, this.currentView, false);
        } else {
            // Modo Estudio Fotográfico Flotante 3D Standalone (Mockups para WhatsApp y Producción)
            // 1. Fondo de estudio con foco de iluminación radial 3D (Spotlight)
            const bgGrad = ctx.createRadialGradient(
                this.baseWidth / 2, this.baseHeight * 0.40, 30,
                this.baseWidth / 2, this.baseHeight * 0.40, this.baseWidth * 0.78
            );
            bgGrad.addColorStop(0, '#FFFFFF');
            bgGrad.addColorStop(0.40, '#F8FAFC');
            bgGrad.addColorStop(0.75, '#E2E8F0');
            bgGrad.addColorStop(1, '#CBD5E1');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, this.baseWidth, this.baseHeight);

            // 2. Proporciones y centrado con márgenes para sombras fotorrealistas sin recortes
            const scale = 0.86;
            const shirtW = Math.round(this.baseWidth * scale); // 516px
            const shirtH = Math.round(this.baseHeight * scale); // 699px
            const shirtX = Math.round((this.baseWidth - shirtW) / 2); // 42px
            const shirtY = 22; // 22px arriba, deja 92px abajo para sombra de levitación

            // 3. Sombra de piso / levitación elíptica 3D
            const groundY = shirtY + shirtH + 18;
            const groundRx = shirtW * 0.38;
            const groundRy = 16;
            const groundGrad = ctx.createRadialGradient(
                this.baseWidth / 2, groundY, 0,
                this.baseWidth / 2, groundY, groundRx
            );
            groundGrad.addColorStop(0, 'rgba(15, 23, 42, 0.45)');
            groundGrad.addColorStop(0.35, 'rgba(15, 23, 42, 0.22)');
            groundGrad.addColorStop(0.70, 'rgba(15, 23, 42, 0.06)');
            groundGrad.addColorStop(1, 'rgba(15, 23, 42, 0)');

            ctx.save();
            ctx.fillStyle = groundGrad;
            ctx.beginPath();
            ctx.ellipse(this.baseWidth / 2, groundY, groundRx, groundRy, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // 4. Doble capa de sombra fotorrealista de flotación 3D detrás de la prenda
            if (tCanvas) {
                // Capa A: Levitación profunda
                ctx.save();
                ctx.shadowColor = 'rgba(15, 23, 42, 0.32)';
                ctx.shadowBlur = 38;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 24;
                ctx.drawImage(tCanvas, shirtX, shirtY, shirtW, shirtH);
                ctx.restore();

                // Capa B: Oclusión cercana
                ctx.save();
                ctx.shadowColor = 'rgba(15, 23, 42, 0.18)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 8;
                ctx.drawImage(tCanvas, shirtX, shirtY, shirtW, shirtH);
                ctx.restore();

                // Capa C: Prenda nítida
                ctx.drawImage(tCanvas, shirtX, shirtY, shirtW, shirtH);
            }

            // 5. Estampado DTF con recorte anatómico exacto sobre la camiseta flotante
            ctx.save();
            ctx.translate(shirtX, shirtY);
            ctx.scale(scale, scale);
            this.renderMaskedStamp(ctx, this.currentView, false);
            ctx.restore();

            // 6. Marca de agua corporativa opcional
            if (addBrandWatermark && this.logoImg && this.logoImg.complete && this.logoImg.naturalWidth > 0) {
                ctx.save();
                const badgeW = 156;
                const badgeH = 46;
                const badgeX = 22;
                const badgeY = 22;

                ctx.shadowColor = 'rgba(15, 23, 42, 0.14)';
                ctx.shadowBlur = 10;
                ctx.shadowOffsetY = 3;
                ctx.fillStyle = 'rgba(255, 255, 255, 0.96)';
                ctx.strokeStyle = '#E2E8F0';
                ctx.lineWidth = 1;

                const r = 12;
                ctx.beginPath();
                ctx.moveTo(badgeX + r, badgeY);
                ctx.lineTo(badgeX + badgeW - r, badgeY);
                ctx.quadraticCurveTo(badgeX + badgeW, badgeY, badgeX + badgeW, badgeY + r);
                ctx.lineTo(badgeX + badgeW, badgeY + badgeH - r);
                ctx.quadraticCurveTo(badgeX + badgeW, badgeY + badgeH, badgeX + badgeW - r, badgeY + badgeH);
                ctx.lineTo(badgeX + r, badgeY + badgeH);
                ctx.quadraticCurveTo(badgeX, badgeY + badgeH, badgeX, badgeY + badgeH - r);
                ctx.lineTo(badgeX, badgeY + r);
                ctx.quadraticCurveTo(badgeX, badgeY, badgeX + r, badgeY);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                ctx.shadowColor = 'transparent';
                const logoSize = 34;
                ctx.drawImage(this.logoImg, badgeX + 6, badgeY + (badgeH - logoSize) / 2, logoSize, logoSize);

                ctx.fillStyle = '#0F172A';
                ctx.font = 'bold 12px "Outfit", sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText('StampCol', badgeX + 46, badgeY + 20);

                ctx.fillStyle = '#FF6B00';
                ctx.font = 'bold 8.5px "Plus Jakarta Sans", sans-serif';
                ctx.fillText('DTF ULTRA HD', badgeX + 46, badgeY + 33);
                ctx.restore();
            }
        }

        const dataUrl = offCanvas.toDataURL('image/png');
        this.currentView = originalView;
        return dataUrl;
    }

    generateCompositeMockup() {
        const compCanvas = document.createElement('canvas');
        compCanvas.width = 1200;
        compCanvas.height = 860;
        const ctx = compCanvas.getContext('2d');

        // Fondo de estudio limpio y corporativo
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, 1200, 860);

        // Borde exterior
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(20, 20, 1160, 820);

        // Encabezado corporativo StampCol idéntico a la plantilla oficial
        ctx.fillStyle = '#0F172A';
        ctx.font = 'bold 28px "Outfit", sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText('StampCol — Hoja de Confección & Mockup Oficial', 45, 68);

        ctx.font = '600 13px "Plus Jakarta Sans", sans-serif';
        ctx.fillStyle = '#64748B';
        const colorName = this.currentColorName || 'Blanco';
        const garmentLabel = (document.getElementById('id_garment_type')?.value || 'Camiseta Cuello Redondo').replace(' Clásica', '');
        const dateStr = new Date().toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
        ctx.fillText(`PRENDA: ${garmentLabel.toUpperCase()}  |  COLOR: ${colorName.toUpperCase()}  |  TÉCNICA: DTF Ultra HD  |  FECHA: ${dateStr}`, 45, 96);

        // Línea divisoria
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(45, 114);
        ctx.lineTo(1155, 114);
        ctx.stroke();

        // Exportar ambas caras limpias (transparentes) para componerlas con marco de estudio flotante
        const frontData = this.getSnapshotBase64('front', false, true);
        const backData = this.getSnapshotBase64('back', false, true);

        return new Promise((resolve) => {
            const imgF = new Image();
            const imgB = new Image();
            let count = 0;
            const done = () => {
                count++;
                if (count === 2) {
                    const cardW = 535;
                    const cardH = 635;
                    const topY = 135;

                    const drawStudioCard = (cardX, img, label) => {
                        ctx.save();

                        // 1. Marco redondeado de estudio fotográfico profesional (radio 24px)
                        const radius = 24;
                        ctx.beginPath();
                        ctx.moveTo(cardX + radius, topY);
                        ctx.lineTo(cardX + cardW - radius, topY);
                        ctx.quadraticCurveTo(cardX + cardW, topY, cardX + cardW, topY + radius);
                        ctx.lineTo(cardX + cardW, topY + cardH - radius);
                        ctx.quadraticCurveTo(cardX + cardW, topY + cardH, cardX + cardW - radius, topY + cardH);
                        ctx.lineTo(cardX + radius, topY + cardH);
                        ctx.quadraticCurveTo(cardX, topY + cardH, cardX, topY + cardH - radius);
                        ctx.lineTo(cardX, topY + radius);
                        ctx.quadraticCurveTo(cardX, topY, cardX + radius, topY);
                        ctx.closePath();

                        // 2. Fondo de estudio con foco de iluminación radial 3D (Spotlight Studio)
                        const spotX = cardX + cardW / 2;
                        const spotY = topY + cardH * 0.40;
                        const studioSpotlight = ctx.createRadialGradient(
                            spotX, spotY, 30,
                            spotX, spotY, cardW * 0.75
                        );
                        studioSpotlight.addColorStop(0, '#FFFFFF');
                        studioSpotlight.addColorStop(0.40, '#F8FAFC');
                        studioSpotlight.addColorStop(0.78, '#E2E8F0');
                        studioSpotlight.addColorStop(1, '#CBD5E1');

                        ctx.fillStyle = studioSpotlight;
                        ctx.fill();

                        ctx.strokeStyle = '#CBD5E1';
                        ctx.lineWidth = 1.5;
                        ctx.stroke();

                        ctx.save();
                        ctx.clip(); // Limitar sombras y efectos dentro del marco

                        // 3. Resplandor superior de iluminación de estudio
                        const topGlow = ctx.createLinearGradient(cardX, topY, cardX, topY + 110);
                        topGlow.addColorStop(0, 'rgba(255, 255, 255, 0.7)');
                        topGlow.addColorStop(1, 'rgba(255, 255, 255, 0)');
                        ctx.fillStyle = topGlow;
                        ctx.fillRect(cardX, topY, cardW, 110);

                        // Dimensiones de la camiseta dentro del estudio (escala armónica con espacio para flotación)
                        const shirtW = 390;
                        const shirtH = Math.round(shirtW * (813 / 600)); // ~528px
                        const shirtX = cardX + Math.round((cardW - shirtW) / 2);
                        const shirtY = topY + 20;

                        // 4. Sombra de piso / levitación elíptica (proyectada en el suelo del estudio)
                        const groundCenterY = shirtY + shirtH + 16;
                        const groundRadiusX = shirtW * 0.38;
                        const groundRadiusY = 16;
                        const groundShadow = ctx.createRadialGradient(
                            spotX, groundCenterY, 0,
                            spotX, groundCenterY, groundRadiusX
                        );
                        groundShadow.addColorStop(0, 'rgba(15, 23, 42, 0.45)');
                        groundShadow.addColorStop(0.35, 'rgba(15, 23, 42, 0.22)');
                        groundShadow.addColorStop(0.70, 'rgba(15, 23, 42, 0.06)');
                        groundShadow.addColorStop(1, 'rgba(15, 23, 42, 0)');

                        ctx.save();
                        ctx.fillStyle = groundShadow;
                        ctx.beginPath();
                        ctx.ellipse(spotX, groundCenterY, groundRadiusX, groundRadiusY, 0, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.restore();

                        // 5. Doble capa de sombra fotorrealista de flotación 3D detrás de la prenda
                        // Capa A: Sombra de levitación profunda que despega la prenda del fondo
                        ctx.save();
                        ctx.shadowColor = 'rgba(15, 23, 42, 0.32)';
                        ctx.shadowBlur = 40;
                        ctx.shadowOffsetX = 0;
                        ctx.shadowOffsetY = 24;
                        ctx.drawImage(img, shirtX, shirtY, shirtW, shirtH);
                        ctx.restore();

                        // Capa B: Sombra de oclusión ambiental cercana
                        ctx.save();
                        ctx.shadowColor = 'rgba(15, 23, 42, 0.18)';
                        ctx.shadowBlur = 14;
                        ctx.shadowOffsetX = 0;
                        ctx.shadowOffsetY = 8;
                        ctx.drawImage(img, shirtX, shirtY, shirtW, shirtH);
                        ctx.restore();

                        // Capa C: Prenda nítida flotando en el estudio
                        ctx.drawImage(img, shirtX, shirtY, shirtW, shirtH);

                        ctx.restore(); // fin del clip

                        // 6. Badge flotante de estudio para el título de la vista
                        const badgeW = 230;
                        const badgeH = 34;
                        const badgeX = cardX + (cardW - badgeW) / 2;
                        const badgeY = topY + cardH - 46;

                        ctx.save();
                        ctx.shadowColor = 'rgba(15, 23, 42, 0.15)';
                        ctx.shadowBlur = 12;
                        ctx.shadowOffsetY = 4;
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                        ctx.strokeStyle = '#E2E8F0';
                        ctx.lineWidth = 1;

                        const br = 17;
                        ctx.beginPath();
                        ctx.moveTo(badgeX + br, badgeY);
                        ctx.lineTo(badgeX + badgeW - br, badgeY);
                        ctx.quadraticCurveTo(badgeX + badgeW, badgeY, badgeX + badgeW, badgeY + br);
                        ctx.lineTo(badgeX + badgeW, badgeY + badgeH - br);
                        ctx.quadraticCurveTo(badgeX + badgeW, badgeY + badgeH, badgeX + badgeW - br, badgeY + badgeH);
                        ctx.lineTo(badgeX + br, badgeY + badgeH);
                        ctx.quadraticCurveTo(badgeX, badgeY + badgeH, badgeX, badgeY + badgeH - br);
                        ctx.lineTo(badgeX, badgeY + br);
                        ctx.quadraticCurveTo(badgeX, badgeY, badgeX + br, badgeY);
                        ctx.closePath();
                        ctx.fill();
                        ctx.stroke();

                        ctx.shadowColor = 'transparent';
                        ctx.fillStyle = '#0F172A';
                        ctx.font = 'bold 12px "Outfit", sans-serif';
                        ctx.textAlign = 'center';
                        ctx.fillText(label, spotX, badgeY + 21);
                        ctx.restore();
                    };

                    drawStudioCard(45, imgF, 'VISTA FRONTAL (PECHO)');
                    drawStudioCard(620, imgB, 'VISTA POSTERIOR (ESPALDA)');

                    // Pie de página corporativo
                    ctx.font = '500 11px "Plus Jakarta Sans", sans-serif';
                    ctx.fillStyle = '#94A3B8';
                    ctx.textAlign = 'left';
                    ctx.fillText('StampCol • Campoalegre, Huila • WhatsApp: 317 153 5408 • @stampcol2025 • Estampado Textil DTF Ultra HD', 45, 830);

                    ctx.textAlign = 'right';
                    ctx.fillText('Documento Oficial de Creación & Confección Textil', 1155, 830);

                    resolve(compCanvas.toDataURL('image/png'));
                }
            };

            imgF.onload = done;
            imgB.onload = done;
            imgF.src = frontData;
            imgB.src = backData;
        });
    }

    async downloadCurrentMockup() {
        const fullDataUrl = await this.generateCompositeMockup();
        const link = document.createElement('a');
        link.download = `stampcol_hoja_confeccion_${(this.currentColorName || 'camiseta').toLowerCase()}_${Date.now()}.png`;
        link.href = fullDataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    async getCompositeBlob() {
        const fullDataUrl = await this.generateCompositeMockup();
        const res = await fetch(fullDataUrl);
        return await res.blob();
    }

    getDesignSourceUrls() {
        const urls = [];
        if (this.layers.front && this.layers.front.hasDesign && this.layers.front.sourceUrl) {
            urls.push(this.layers.front.sourceUrl);
        }
        if (this.layers.back && this.layers.back.hasDesign && this.layers.back.sourceUrl && !urls.includes(this.layers.back.sourceUrl)) {
            urls.push(this.layers.back.sourceUrl);
        }
        return urls;
    }

    async printMockup() {
        const fullDataUrl = await this.generateCompositeMockup();
        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            // Alternativa si el navegador bloquea ventanas emergentes
            const iframe = document.createElement('iframe');
            iframe.style.position = 'fixed';
            iframe.style.right = '0';
            iframe.style.bottom = '0';
            iframe.style.width = '0';
            iframe.style.height = '0';
            iframe.style.border = '0';
            document.body.appendChild(iframe);
            const doc = iframe.contentWindow.document;
            doc.open();
            doc.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>StampCol — Hoja de Confección & Mockup Oficial</title>
                    <style>
                        @page { size: landscape; margin: 0; }
                        body { margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; background: #fff; }
                        img { max-width: 100%; height: auto; display: block; margin: auto; }
                    </style>
                </head>
                <body>
                    <img src="${fullDataUrl}" />
                    <script>
                        window.onload = function() {
                            setTimeout(function() {
                                window.focus();
                                window.print();
                            }, 300);
                        };
                    <\/script>
                </body>
                </html>
            `);
            doc.close();
            return;
        }
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>StampCol — Hoja de Confección & Mockup Oficial</title>
                <style>
                    @page { size: landscape; margin: 0; }
                    body { margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; background: #f8fafc; }
                    img { max-width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); background: #ffffff; }
                    @media print {
                        body { padding: 0; background: #fff; }
                        img { border: none; box-shadow: none; max-width: 100%; width: 100%; }
                    }
                </style>
            </head>
            <body>
                <img src="${fullDataUrl}" alt="StampCol — Hoja de Confección & Mockup Oficial" />
                <script>
                    window.onload = function() {
                        setTimeout(function() {
                            window.focus();
                            window.print();
                        }, 300);
                    };
                <\/script>
            </body>
            </html>
        `);
        printWindow.document.close();
    }

    triggerViewChangeUI(viewName) {
        const btnFront = document.getElementById('btn-view-front');
        const btnBack = document.getElementById('btn-view-back');
        if (btnFront && btnBack) {
            if (viewName === 'front') {
                btnFront.classList.add('bg-amber-500', 'text-slate-950', 'shadow-xs');
                btnFront.classList.remove('bg-transparent', 'text-slate-600', 'hover:text-slate-900');
                btnBack.classList.remove('bg-amber-500', 'text-slate-950', 'shadow-xs');
                btnBack.classList.add('bg-transparent', 'text-slate-600', 'hover:text-slate-900');
            } else {
                btnBack.classList.add('bg-amber-500', 'text-slate-950', 'shadow-xs');
                btnBack.classList.remove('bg-transparent', 'text-slate-600', 'hover:text-slate-900');
                btnFront.classList.remove('bg-amber-500', 'text-slate-950', 'shadow-xs');
                btnFront.classList.add('bg-transparent', 'text-slate-600', 'hover:text-slate-900');
            }
        }

        // Actualizar indicador de capa en el visor
        const viewBadge = document.getElementById('current-view-badge');
        if (viewBadge) {
            const vista = viewName === 'front' ? 'Frente' : 'Espalda';
            viewBadge.textContent = `Camiseta • ${vista}`;
        }

        // Sincronizar botón de alternar vista en barra inferior móvil
        const mobText = document.getElementById('mobile-toggle-view-text');
        if (mobText) {
            mobText.textContent = (viewName === 'front') ? 'Ver Espalda' : 'Ver Frente';
        }

        this.syncControlsUI();
    }

    syncBackgroundButtonUI() {
        const layer = this.getCurrentLayer();
        const btn = document.getElementById('btn-toggle-bg-action') || document.getElementById('btn-ai-clean-bg-quick');
        if (!btn) return;

        if (!layer || !layer.hasDesign) {
            btn.classList.add('opacity-50', 'pointer-events-none');
            btn.innerHTML = '<span>✂️ Quitar Fondo (Opcional)</span>';
            return;
        }

        btn.classList.remove('opacity-50', 'pointer-events-none');
        if (layer.isBackgroundRemoved) {
            btn.innerHTML = '<span>🖼️ Mantener Fondo Original</span>';
            btn.className = 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold transition shadow-xs text-xs cursor-pointer active:scale-95 border border-slate-700';
            btn.title = 'Haz clic para restaurar el fondo de tu foto o imagen original';
        } else {
            btn.innerHTML = '<span>✂️ Quitar Fondo (Opcional)</span>';
            btn.className = 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition shadow-xs text-xs cursor-pointer active:scale-95';
            btn.title = 'Hacer el fondo transparente para estampado DTF';
        }
    }

    async toggleBackground(forceState = null) {
        const layer = this.getCurrentLayer();
        if (!layer || !layer.hasDesign) return;

        const targetState = (forceState !== null) ? Boolean(forceState) : !layer.isBackgroundRemoved;
        const btn = document.getElementById('btn-toggle-bg-action') || document.getElementById('btn-ai-clean-bg-quick');

        if (targetState === false) {
            // Restaurar fondo original
            layer.isBackgroundRemoved = false;
            const targetUrl = layer.rawOriginalSrc || layer.imgSrc;

            if (layer.appliedShape) {
                this.applyShape(layer.appliedShape);
            } else {
                const currentX = layer.x;
                const currentY = layer.y;
                const currentScale = layer.scale;
                const currentRot = layer.rotation;
                this.setDesignFromUrl(targetUrl, this.currentView, {
                    preserveHistory: true,
                    preserveTransform: true
                });
                setTimeout(() => {
                    layer.x = currentX;
                    layer.y = currentY;
                    layer.scale = currentScale;
                    layer.rotation = currentRot;
                    this.syncControlsUI();
                    this.render();
                }, 60);
            }
            this.syncBackgroundButtonUI();

            const notice = document.createElement('div');
            notice.className = 'fixed bottom-20 right-6 z-50 bg-slate-900 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom duration-200 flex items-center gap-2';
            notice.innerHTML = `<span>🖼️</span> ¡Fondo original restaurado!`;
            document.body.appendChild(notice);
            setTimeout(() => notice.remove(), 3000);
            return;
        }

        // Si se pide aislar el fondo (targetState === true):
        if (layer.isolatedSrc) {
            layer.isBackgroundRemoved = true;
            if (layer.appliedShape) {
                this.applyShape(layer.appliedShape);
            } else {
                const currentX = layer.x;
                const currentY = layer.y;
                const currentScale = layer.scale;
                const currentRot = layer.rotation;
                this.setDesignFromUrl(layer.isolatedSrc, this.currentView, {
                    preserveHistory: true,
                    preserveTransform: true
                });
                setTimeout(() => {
                    layer.x = currentX;
                    layer.y = currentY;
                    layer.scale = currentScale;
                    layer.rotation = currentRot;
                    this.syncControlsUI();
                    this.render();
                }, 60);
            }
            this.syncBackgroundButtonUI();

            const notice = document.createElement('div');
            notice.className = 'fixed bottom-20 right-6 z-50 bg-slate-900 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom duration-200 flex items-center gap-2';
            notice.innerHTML = `<span>✂️</span> ¡Fondo eliminado con transparencia DTF!`;
            document.body.appendChild(notice);
            setTimeout(() => notice.remove(), 3000);
            return;
        }

        // Petición al servidor para aislar el fondo
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span>⏳ Quitando fondo...</span>';
        }

        function getCsrf() {
            const match = document.cookie.match(/csrftoken=([^;]+)/);
            return match ? match[1] : '';
        }

        try {
            const srcToProcess = layer.rawOriginalSrc || layer.imgSrc;
            const res = await fetch('/api/isolate-stamp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf()
                },
                body: JSON.stringify({
                    image_base64: srcToProcess,
                    tolerance: 38
                })
            });

            const data = await res.json();
            const isolatedResult = data.isolated_image || data.isolated_stamp_base64;
            if (data.status === 'success' && isolatedResult) {
                layer.isolatedSrc = isolatedResult;
                const isoImg = new Image();
                isoImg.crossOrigin = 'anonymous';
                isoImg.onload = () => {
                    layer.isolatedImage = isoImg;
                    layer.isBackgroundRemoved = true;

                    if (layer.appliedShape) {
                        this.applyShape(layer.appliedShape);
                    } else {
                        const currentX = layer.x;
                        const currentY = layer.y;
                        const currentScale = layer.scale;
                        const currentRot = layer.rotation;
                        this.setDesignFromUrl(isolatedResult, this.currentView, {
                            preserveHistory: true,
                            preserveTransform: true
                        });
                        setTimeout(() => {
                            layer.x = currentX;
                            layer.y = currentY;
                            layer.scale = currentScale;
                            layer.rotation = currentRot;
                            this.syncControlsUI();
                            this.render();
                        }, 60);
                    }
                    this.syncBackgroundButtonUI();
                };
                isoImg.src = isolatedResult;

                const notice = document.createElement('div');
                notice.className = 'fixed bottom-20 right-6 z-50 bg-slate-900 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom duration-200 flex items-center gap-2';
                notice.innerHTML = `<span>✂️</span> ¡Fondo eliminado con transparencia DTF!`;
                document.body.appendChild(notice);
                setTimeout(() => notice.remove(), 3000);
            } else {
                alert(data.message || 'No fue posible aislar el fondo de esta imagen.');
            }
        } catch (err) {
            console.error('Error al aislar fondo:', err);
            alert('Error al conectar con el servidor.');
        } finally {
            if (btn) btn.disabled = false;
            this.syncBackgroundButtonUI();
        }
    }

    duplicateToOppositeView() {
        const currentLayer = this.getCurrentLayer();
        if (!currentLayer || !currentLayer.hasDesign || !currentLayer.imgSrc) return;

        const oppositeView = (this.currentView === 'front') ? 'back' : 'front';
        const oppLayer = this.layers[oppositeView];

        oppLayer.img = currentLayer.img;
        oppLayer.imgSrc = currentLayer.imgSrc;
        oppLayer.rawOriginalSrc = currentLayer.rawOriginalSrc;
        oppLayer.rawOriginalImage = currentLayer.rawOriginalImage;
        oppLayer.isolatedSrc = currentLayer.isolatedSrc;
        oppLayer.isolatedImage = currentLayer.isolatedImage;
        oppLayer.isBackgroundRemoved = currentLayer.isBackgroundRemoved;
        oppLayer.appliedShape = currentLayer.appliedShape;
        oppLayer.hasDesign = true;
        oppLayer.width = currentLayer.width;
        oppLayer.height = currentLayer.height;
        oppLayer.scale = currentLayer.scale;
        oppLayer.rotation = currentLayer.rotation;
        oppLayer.x = 300;
        oppLayer.y = (oppositeView === 'front') ? 370 : 390;

        this.setView(oppositeView);
        this.syncControlsUI();
        this.render();

        const notice = document.createElement('div');
        notice.className = 'fixed bottom-20 right-6 z-50 bg-slate-900 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom duration-200 flex items-center gap-2';
        notice.innerHTML = `<span>🔄</span> ¡Diseño duplicado en ${oppositeView === 'front' ? 'el Frente' : 'la Espalda'}!`;
        document.body.appendChild(notice);
        setTimeout(() => notice.remove(), 3000);
    }

    syncControlsUI() {
        const layer = this.getCurrentLayer();
        const scaleRange = document.getElementById('design-scale-slider');
        const rotateRange = document.getElementById('design-rotate-slider');
        const designControls = document.getElementById('active-design-controls');
        const hasDesignDotFront = document.getElementById('design-indicator-front');
        const hasDesignDotBack = document.getElementById('design-indicator-back');

        if (hasDesignDotFront) {
            hasDesignDotFront.classList.toggle('hidden', !this.layers.front.hasDesign);
        }
        if (hasDesignDotBack) {
            hasDesignDotBack.classList.toggle('hidden', !this.layers.back.hasDesign);
        }

        if (designControls) {
            if (layer.hasDesign) {
                designControls.classList.remove('hidden');
            } else {
                designControls.classList.add('hidden');
            }
        }

        const activeThumb = document.getElementById('active-design-thumbnail');
        const activeIcon = document.getElementById('active-design-icon-placeholder');
        const activeViewLabel = document.getElementById('active-design-view-label');
        if (activeViewLabel) {
            activeViewLabel.textContent = `Vista: ${this.currentView === 'front' ? 'Frente' : 'Espalda'}`;
        }
        if (activeThumb && activeIcon) {
            if (layer.hasDesign && (layer.isolatedSrc || layer.imgSrc)) {
                activeThumb.src = layer.isolatedSrc || layer.imgSrc;
                activeThumb.classList.remove('hidden');
                activeIcon.classList.add('hidden');
            } else {
                activeThumb.src = '';
                activeThumb.classList.add('hidden');
                activeIcon.classList.remove('hidden');
            }
        }
        if (scaleRange) scaleRange.value = layer.scale;
        const scaleDisplay = document.getElementById('scale-value-display');
        if (scaleDisplay) scaleDisplay.textContent = `${Math.round(layer.scale * 100)}%`;
        if (rotateRange) rotateRange.value = layer.rotation;
        const rotateDisplay = document.getElementById('rotate-value-display');
        if (rotateDisplay) rotateDisplay.textContent = `${Math.round(layer.rotation)}°`;

        this.syncBackgroundButtonUI();
    }

    setCustomTouchedUpDesign(dataUrl) {
        if (!dataUrl) return;
        const layer = this.getCurrentLayer();
        if (!layer) return;

        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            layer.img = img;
            layer.imgSrc = dataUrl;
            layer.isolatedSrc = dataUrl;
            layer.isolatedImage = img;
            layer.isBackgroundRemoved = true;
            this.syncControlsUI();
            this.render();

            try {
                window.dispatchEvent(new CustomEvent('stampcol:design-changed', {
                    detail: { url: dataUrl, view: this.currentView }
                }));
            } catch (e) {}
        };
        img.src = dataUrl;
    }
}


window.HoodieCustomizer = HoodieCustomizer;

window.toggleMobileView = function() {
    if (!window.customizer) return;
    const target = (window.customizer.currentView === 'front') ? 'back' : 'front';
    window.customizer.setView(target);
};
