// Variáveis globais para o carrossel
let currentSlideIndex = 0;
let slides;
let indicators;
let totalSlides;

// Função para inicializar o carrossel
function initializeCarousel() {
    slides = document.querySelectorAll(".carousel-slide");
    indicators = document.querySelectorAll(".indicator");
    totalSlides = slides.length;

    if (totalSlides > 0) {
        showSlide(0);
        // Auto-play a cada 6 segundos (opcional - remova se não quiser)
        setInterval(autoPlay, 6000);
    }
}

// Função para mostrar slide específico
function showSlide(index) {
    if (!slides || !indicators) return; // Garante que os elementos existem

    // Remove classe active de todos os slides e indicadores
    slides.forEach(slide => slide.classList.remove("active"));
    indicators.forEach(indicator => indicator.classList.remove("active"));
    
    // Adiciona classe active ao slide e indicador atual
    slides[index].classList.add("active");
    indicators[index].classList.add("active");
    
    currentSlideIndex = index;
}

// Função para mudar slide (próximo/anterior)
function changeSlide(direction) {
    currentSlideIndex += direction;
    
    // Loop infinito
    if (currentSlideIndex >= totalSlides) {
        currentSlideIndex = 0;
    } else if (currentSlideIndex < 0) {
        currentSlideIndex = totalSlides - 1;
    }
    
    showSlide(currentSlideIndex);
}

// Função para ir para slide específico
function currentSlide(index) {
    showSlide(index - 1); // -1 porque o índice começa em 0
}

// Auto-play do carrossel (opcional)
function autoPlay() {
    changeSlide(1);
}

// Inicializar carrossel quando a página carregar
document.addEventListener("DOMContentLoaded", initializeCarousel);

// Pausar auto-play quando mouse estiver sobre o carrossel
const carouselContainer = document.querySelector(".carousel-container");
let autoPlayInterval;

if (carouselContainer) {
    carouselContainer.addEventListener("mouseenter", function() {
        clearInterval(autoPlayInterval);
    });
    
    carouselContainer.addEventListener("mouseleave", function() {
        autoPlayInterval = setInterval(autoPlay, 5000);
    });
}
