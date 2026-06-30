document.querySelectorAll(".campo_data input").forEach(input => {
    const campo = input.parentElement;
    const label = campo.querySelector("label");
    function atualizarCampo() {
        if (input.value) {
            input.classList.add("tem_valor");
            label.classList.add("escondida");
        } else {
            input.classList.remove("tem_valor");
            if (document.activeElement !== input) {
                label.classList.remove("escondida");
            }
        }
    }
    input.addEventListener("focus", () => {
        label.classList.add("escondida");
    });
    input.addEventListener("blur", () => {
        atualizarCampo();
    });
    input.addEventListener("change", atualizarCampo);
    input.addEventListener("input", atualizarCampo);
    atualizarCampo();
});