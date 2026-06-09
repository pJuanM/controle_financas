function mostrarQuantidadeParcelas() {
    const select = document.getElementById("parcelado");
    const qntParcelas = document.getElementById("qnt_parcelas");

    if (select.value === "true") {
        qntParcelas.style.display = "block";       
        qntParcelas.required = true;
    } else {
        qntParcelas.required = false;
        qntParcelas.style.display = "none";

    }
}