// Função para abrir o modal
function contactSupport() {
    document.getElementById("contact-modal").style.display = "block";
}

// Função para fechar o modal
function closeContactModal() {
    document.getElementById("contact-modal").style.display = "none";
}

// Fecha o modal ao clicar fora da área de conteúdo
window.onclick = function(event) {
    const modal = document.getElementById("contact-modal");
    if (event.target === modal) {
        closeContactModal();
    }
}
