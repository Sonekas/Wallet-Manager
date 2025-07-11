// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            }
        });
    });
    
    // Header background on scroll
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = 'none';
        }
    });
    
    // Animate stats on scroll
    const stats = document.querySelectorAll('.stat-number');
    let statsAnimated = false;
    
    const animateStats = () => {
        if (statsAnimated) return;
        
        stats.forEach(stat => {
            const rect = stat.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const finalValue = stat.textContent;
                const isPercentage = finalValue.includes('%');
                const isPlus = finalValue.includes('+');
                const numericValue = parseInt(finalValue.replace(/[^\d]/g, ''));
                
                if (!isNaN(numericValue)) {
                    let currentValue = 0;
                    const increment = numericValue / 50;
                    
                    const timer = setInterval(() => {
                        currentValue += increment;
                        if (currentValue >= numericValue) {
                            currentValue = numericValue;
                            clearInterval(timer);
                        }
                        
                        let displayValue = Math.floor(currentValue);
                        if (isPercentage) displayValue += '%';
                        if (isPlus && displayValue > 0) displayValue = '+' + displayValue;
                        
                        stat.textContent = displayValue;
                    }, 20);
                }
                statsAnimated = true;
            }
        });
    };
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Animate stats when hero section is visible
                if (entry.target.classList.contains('hero-stats')) {
                    animateStats();
                }
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.feature-card, .tech-item, .hero-stats, .screenshot-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Screenshot modal functionality
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const modalCaption = document.getElementById('modalCaption');
    const closeModal = document.querySelector('.close');
    
    // Add click event to all screenshot items
    const screenshotItems = document.querySelectorAll('.screenshot-item');
    screenshotItems.forEach(item => {
        item.addEventListener('click', function() {
            const img = this.querySelector('.screenshot-image');
            const overlay = this.querySelector('.screenshot-overlay');
            
            if (img && img.src) {
                modal.style.display = 'block';
                modalImg.src = img.src;
                modalCaption.textContent = overlay ? overlay.querySelector('h4').textContent : img.alt;
            }
        });
    });
    
    // Close modal functionality
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside the image
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Feature card hover effects
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Button click effects
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Parallax effect for hero background
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroParticles = document.querySelector('.hero-particles');
        
        if (heroParticles) {
            heroParticles.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
    
    // Video controls
    const demoVideo = document.querySelector('.demo-video-player');
    const videoOverlay = document.querySelector('.video-overlay');
    const playButtonLarge = document.querySelector('.play-button-large');
    
    if (demoVideo && playButtonLarge) {
        playButtonLarge.addEventListener('click', function() {
            demoVideo.play();
            videoOverlay.style.opacity = '0';
        });
        
        demoVideo.addEventListener('play', function() {
            videoOverlay.style.opacity = '0';
        });
        
        demoVideo.addEventListener('pause', function() {
            videoOverlay.style.opacity = '1';
        });
        
        demoVideo.addEventListener('ended', function() {
            videoOverlay.style.opacity = '1';
        });
    }
    
    // Hero app preview click to scroll to demo video
    const appPreview = document.querySelector('.app-preview');
    if (appPreview) {
        appPreview.addEventListener('click', function() {
            const demoSection = document.querySelector('#demo-video');
            if (demoSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = demoSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    // Feature cards stagger animation
    const featureCardsForAnimation = document.querySelectorAll('.feature-card');
    featureCardsForAnimation.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Tech items stagger animation
    const techItems = document.querySelectorAll('.tech-item');
    techItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Download button tracking (placeholder for analytics)
    const downloadButtons = document.querySelectorAll('a[href="#"]');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Show download modal or redirect to actual download
            const buttonText = this.textContent.trim();
            
            if (buttonText.includes('Windows')) {
                alert('Download para Windows será iniciado em breve!\n\nEm uma implementação real, aqui seria o link para o arquivo .exe');
            } else if (buttonText.includes('GitHub')) {
                alert('Redirecionando para o repositório GitHub!\n\nEm uma implementação real, aqui seria o link para o repositório');
            } else {
                alert('Download será iniciado em breve!');
            }
        });
    });
    
    // Lazy loading for images
    const images = document.querySelectorAll('img[src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '0';
                img.style.transition = 'opacity 0.3s ease';
                
                img.onload = function() {
                    this.style.opacity = '1';
                };
                
                // If image is already loaded
                if (img.complete) {
                    img.style.opacity = '1';
                }
                
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        imageObserver.observe(img);
    });
    
    // Error handling for missing images
    images.forEach(img => {
        img.addEventListener('error', function() {
            // Create a placeholder for missing images
            const placeholder = document.createElement('div');
            placeholder.style.width = '100%';
            placeholder.style.height = this.style.height || '200px';
            placeholder.style.background = 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%)';
            placeholder.style.display = 'flex';
            placeholder.style.alignItems = 'center';
            placeholder.style.justifyContent = 'center';
            placeholder.style.color = '#718096';
            placeholder.style.fontSize = '14px';
            placeholder.style.borderRadius = '8px';
            placeholder.innerHTML = '<i class="fas fa-image" style="margin-right: 8px;"></i>Imagem será adicionada em breve';
            
            this.parentNode.replaceChild(placeholder, this);
        });
    });
    
    // Scroll to top functionality
    const scrollToTopBtn = document.createElement('button');
    scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollToTopBtn.className = 'scroll-to-top';
    scrollToTopBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease, transform 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;
    
    document.body.appendChild(scrollToTopBtn);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.style.opacity = '1';
            scrollToTopBtn.style.transform = 'translateY(0)';
        } else {
            scrollToTopBtn.style.opacity = '0';
            scrollToTopBtn.style.transform = 'translateY(10px)';
        }
    });
    
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Add CSS for ripple effect and mobile menu
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .nav-menu.active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        gap: 1rem;
    }
    
    .nav-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }
    
    .nav-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .nav-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }
    
    @media (max-width: 768px) {
        .nav-menu {
            display: none;
        }
    }
    
    .scroll-to-top:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
    }
`;
document.head.appendChild(style);

