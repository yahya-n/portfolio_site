document.addEventListener('DOMContentLoaded', function () {

    // Fallback: Make everything visible if GSAP fails or takes too long
    setTimeout(() => {
        document.querySelectorAll('.hero-subtitle, .hero-title, .hero-role, .hero-description, .hero-image-wrapper, .navbar, .section-title, .skill-tag, .education-card, .project-card, .cert-card, .premium-contact-card').forEach(el => {
            if (getComputedStyle(el).opacity === '0') {
                el.style.opacity = '1';
                el.style.transform = 'none';
            }
        });
    }, 3000);

    try {
        // Check if GSAP is loaded
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
            console.error('GSAP or ScrollTrigger not loaded');
            return;
        }

        // Register GSAP ScrollTrigger
        gsap.registerPlugin(ScrollTrigger);

        // =============================================
        // CUSTOM CURSOR
        // =============================================
        const cursorDot = document.createElement('div');
        const cursorOutline = document.createElement('div');
        cursorDot.className = 'cursor-dot';
        cursorOutline.className = 'cursor-outline';
        document.body.appendChild(cursorDot);
        document.body.appendChild(cursorOutline);

        // Safely hide default cursor only when custom cursor is active
        document.body.classList.add('custom-cursor-active');

        window.addEventListener('mousemove', (e) => {
            const posX = e.clientX;
            const posY = e.clientY;

            // Dot follows instantly
            cursorDot.style.left = `${posX}px`;
            cursorDot.style.top = `${posY}px`;

            // Outline follows with delay (using GSAP for smoothness)
            gsap.to(cursorOutline, {
                x: posX,
                y: posY,
                duration: 0.15,
                ease: "power2.out"
            });
        });

        // Hover effects for cursor
        const hoverTargets = document.querySelectorAll('a, button, .btn-custom, .btn-outline-custom, .cert-card, .project-card');
        hoverTargets.forEach(el => {
            el.addEventListener('mouseenter', () => document.body.classList.add('hovering'));
            el.addEventListener('mouseleave', () => document.body.classList.remove('hovering'));
        });

        // =============================================
        // HERO ANIMATIONS
        // =============================================
        const tl = gsap.timeline();

        tl.from('.hero-subtitle', {
            y: 20,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out"
        })
            .from('.hero-title', {
                y: 30,
                opacity: 0,
                duration: 1,
                ease: "power3.out"
            }, "-=0.6")
            .from('.hero-role', {
                y: 20,
                opacity: 0,
                duration: 0.8,
                ease: "power3.out"
            }, "-=0.6")
            .from('.hero-description', {
                y: 20,
                opacity: 0,
                duration: 0.8,
                ease: "power3.out"
            }, "-=0.6")
            .from('.hero-section .btn-custom, .hero-section .btn-outline-custom', {
                y: 20,
                opacity: 0,
                duration: 0.8,
                stagger: 0.2,
                ease: "power3.out"
            }, "-=0.6")
            .from('.hero-image-wrapper', {
                scale: 0.8,
                opacity: 0,
                duration: 1.2,
                ease: "back.out(1.7)"
            }, "-=1");

        // Navbar Animation
        gsap.from('.navbar', {
            y: -100,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            delay: 0.5
        });

        // =============================================
        // SCROLL ANIMATIONS
        // =============================================

        // About Section
        gsap.from('#about .section-title', {
            scrollTrigger: {
                trigger: '#about',
                start: "top 80%"
            },
            y: 50,
            opacity: 0,
            duration: 1,
            ease: "power3.out"
        });

        gsap.from('.skill-tag', {
            scrollTrigger: {
                trigger: '#about',
                start: "top 75%"
            },
            y: 20,
            opacity: 0,
            duration: 0.5,
            stagger: 0.05,
            ease: "back.out(1.7)"
        });

        gsap.from('.education-card', {
            scrollTrigger: {
                trigger: '.education-card',
                start: "top 85%"
            },
            x: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power3.out"
        });

        // Projects & Certifications (Grid Reveal)
        const scrollContainers = document.querySelectorAll('.horizontal-scroll-container');
        scrollContainers.forEach(container => {
            gsap.from(container.children, {
                scrollTrigger: {
                    trigger: container,
                    start: "top 85%"
                },
                y: 50, // Changed from x: 100 to y: 50 for a nice upward float
                opacity: 0,
                duration: 0.8,
                stagger: 0.1,
                ease: "power3.out"
            });
        });

        // Contact Section
        gsap.from('.premium-contact-card, .premium-social-card, .premium-form-card', {
            scrollTrigger: {
                trigger: '#contact',
                start: "top 80%"
            },
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power3.out"
        });

        // =============================================
        // 3D TILT EFFECT
        // =============================================
        const tiltCards = document.querySelectorAll('.project-card, .cert-card');

        tiltCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -5; // Max 5deg rotation
                const rotateY = ((x - centerX) / centerX) * 5;

                gsap.to(card, {
                    rotationX: rotateX,
                    rotationY: rotateY,
                    transformPerspective: 1000,
                    duration: 0.4,
                    ease: "power2.out"
                });
            });

            card.addEventListener('mouseleave', () => {
                gsap.to(card, {
                    rotationX: 0,
                    rotationY: 0,
                    duration: 0.7,
                    ease: "elastic.out(1, 0.5)"
                });
            });
        });

        // Navbar Scroll Effect (Glassmorphism enhancement)
        // NAVBAR SHRINK ON SCROLL
        window.addEventListener("scroll", () => {
            const nav = document.querySelector(".navbar");
            if (window.scrollY > 80) {
                nav.classList.add("shrink");
            } else {
                nav.classList.remove("shrink");
            }
        });

        // AUTO ACTIVE LINK HIGHLIGHT BASED ON SCROLL
        const sections = document.querySelectorAll("section[id]");
        const navLinks = document.querySelectorAll(".nav-link");

        window.addEventListener("scroll", () => {
            let scrollPos = window.pageYOffset + 150;

            sections.forEach((sec) => {
                if (scrollPos >= sec.offsetTop && scrollPos < sec.offsetTop + sec.offsetHeight) {
                    let id = sec.getAttribute("id");

                    navLinks.forEach((link) => {
                        link.classList.remove("active");
                        if (link.getAttribute("href").includes(id)) {
                            link.classList.add("active");
                        }
                    });
                }
            });
        });

    });
}
