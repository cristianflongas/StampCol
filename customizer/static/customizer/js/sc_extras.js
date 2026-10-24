/**
 * StampCol - Funcionalidades de Interacción para Secciones de Contenido
 * Aislado en IIFE para no generar variables globales.
 */

(() => {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // 1. Acordeón accesible para FAQs
        const faqTriggers = document.querySelectorAll('.sc-faq-trigger');
        faqTriggers.forEach((trigger) => {
            trigger.addEventListener('click', () => {
                const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
                const targetId = trigger.getAttribute('aria-controls');
                const content = document.getElementById(targetId);

                // Alternar estado actual
                trigger.setAttribute('aria-expanded', !isExpanded);
                if (content) {
                    content.hidden = isExpanded;
                }
            });
        });

        // 2. Animación de Contadores Numéricos al entrar en pantalla
        const counters = document.querySelectorAll('.sc-counter-animate');
        if ('IntersectionObserver' in window && counters.length > 0) {
            const counterObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const el = entry.target;
                        const targetValue = parseInt(el.getAttribute('data-target'), 10);
                        if (!isNaN(targetValue)) {
                            animateNumber(el, targetValue);
                        }
                        observer.unobserve(el);
                    }
                });
            }, { threshold: 0.4 });

            counters.forEach((c) => counterObserver.observe(c));
        }

        function animateNumber(element, finalValue, duration = 1400) {
            let start = 0;
            const startTime = performance.now();

            function updateCounter(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                // Easing out cubic
                const easeProgress = 1 - Math.pow(1 - progress, 3);
                const current = Math.floor(easeProgress * finalValue);
                element.textContent = current;

                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = finalValue;
                }
            }

            requestAnimationFrame(updateCounter);
        }

        // 3. Conexión de Chips de Ideas Rápidas al input de Gemini existente
        const promptInput = document.getElementById('gemini-user-prompt');
        const scIdeaChips = document.querySelectorAll('.sc-quick-idea-chip');

        scIdeaChips.forEach((chip) => {
            chip.addEventListener('click', () => {
                const text = chip.getAttribute('data-idea');
                if (promptInput && text) {
                    promptInput.value = text;
                    promptInput.focus();

                    // Scroll suave hacia el chat si está fuera de pantalla
                    const chatSection = document.getElementById('gemini-chat-section');
                    if (chatSection) {
                        chatSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }
            });
        });

        // 4. Cierre del Banner de Temporada
        const closeBannerBtn = document.getElementById('sc-close-seasonal-banner');
        const seasonalBanner = document.getElementById('sc-seasonal-banner-container');
        if (closeBannerBtn && seasonalBanner) {
            closeBannerBtn.addEventListener('click', () => {
                seasonalBanner.style.display = 'none';
            });
        }

        // 5. Controlador del Slider / Carousel de Soluciones & Colecciones
        const sliderTrack = document.getElementById('sc-solutions-slider');
        const prevBtn = document.getElementById('sc-slider-prev');
        const nextBtn = document.getElementById('sc-slider-next');
        const dotsContainer = document.getElementById('sc-slider-dots');

        if (sliderTrack) {
            const cards = sliderTrack.querySelectorAll('.sc-slider-card');
            
            // Crear indicadores de puntos
            if (dotsContainer && cards.length > 0) {
                dotsContainer.innerHTML = '';
                cards.forEach((_, idx) => {
                    const dot = document.createElement('button');
                    dot.type = 'button';
                    dot.className = `sc-slider-dot ${idx === 0 ? 'active' : ''}`;
                    dot.setAttribute('aria-label', `Ir a diapositiva ${idx + 1}`);
                    dot.addEventListener('click', () => {
                        const cardWidth = cards[0].offsetWidth + 24;
                        sliderTrack.scrollTo({ left: idx * cardWidth, behavior: 'smooth' });
                    });
                    dotsContainer.appendChild(dot);
                });
            }

            const updateDots = () => {
                if (!dotsContainer || cards.length === 0) return;
                const cardWidth = cards[0].offsetWidth + 24;
                const activeIndex = Math.min(cards.length - 1, Math.max(0, Math.round(sliderTrack.scrollLeft / cardWidth)));
                const dots = dotsContainer.querySelectorAll('.sc-slider-dot');
                dots.forEach((d, i) => {
                    if (i === activeIndex) d.classList.add('active');
                    else d.classList.remove('active');
                });
            };

            sliderTrack.addEventListener('scroll', updateDots, { passive: true });

            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    const cardWidth = (cards[0] ? cards[0].offsetWidth : 360) + 24;
                    sliderTrack.scrollBy({ left: -cardWidth, behavior: 'smooth' });
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    const cardWidth = (cards[0] ? cards[0].offsetWidth : 360) + 24;
                    sliderTrack.scrollBy({ left: cardWidth, behavior: 'smooth' });
                });
            }
        }
    });
})();
