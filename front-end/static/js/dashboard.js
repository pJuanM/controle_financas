// GRÁFICO DE LINHA - CUSTOS POR DIA - BASEADO NO MÊS (VENCIMENTO JULHO - COMPRAS QUE VENCE EM JULHO PORÉM COM DATA DE COMPRA DE OUTROS MESES)

Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
Chart.defaults.color = "#717171";
Chart.defaults.borderColor = "#D9E2E8";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 20;
Chart.defaults.plugins.tooltip.backgroundColor = "#000E32";
Chart.defaults.plugins.tooltip.titleColor = "#FFFFFF";
Chart.defaults.plugins.tooltip.bodyColor = "#D9F0EE";
Chart.defaults.plugins.tooltip.borderColor = "#06C1AF";
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

const dashboard = window.dashboard;
const labelsGastosDia = dashboard.label_gastos_dia;
const data_gastos_dia = dashboard.data_gastos_dia;

try {

    const canvas = document.getElementById("gastosDia");
    const ctx = canvas.getContext("2d");

    const gradient = ctx.createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, "rgba(6, 193, 174, 0.62)");
    gradient.addColorStop(1, "rgba(6, 193, 174, 0.22)");

    const dataGastosDia = {
        labels: labelsGastosDia,
        datasets: [{
            label: "Gastos por dia",
            data: data_gastos_dia,
            fill: true,

            backgroundColor: gradient,
            borderColor: "#06C1AF",

            borderWidth: 3,
            tension: 0.35,

            pointBackgroundColor: "#FFFFFF",
            pointBorderColor: "#06C1AF",
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 10
        }]
        
    };
    
    const configGastosDia = {
        type: "line",   
        data: dataGastosDia
    };
    new Chart(
        document.getElementById("gastosDia"),
        configGastosDia
    );


    // GRÁFICO DE COLUNA - CUSTOS X GANHO MÊS A MÊS
    const labelsMes = dashboard.labels_mes;
    const data_gastos_mes = dashboard.data_gastos_mes;
    const data_creditos_mes = dashboard.data_creditos_mes;
    
    const dataGastosMes = {
        labels: labelsMes,
        datasets: [
            {
                label: "Gastos por mês",
                data: data_gastos_mes,

                backgroundColor: "rgba(220, 53, 69, 0.75)",
                borderColor: "#DC3545",

                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            },
            {
                label: "Créditos por mês",
                data: data_creditos_mes,

                backgroundColor: "rgba(40, 167, 69, 0.75)",
                borderColor: "#28A745",

                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false
            }
        ]
    };
    const configGastosMes = {
        type: 'bar',
        data: dataGastosMes,
        options: {
            scales: {
            y: {
                beginAtZero: true
            }
            }
        },
    };
    new Chart(
        document.getElementById("gastosMes"),
        configGastosMes
    );


    // GRÁFICO DE BARRA HORIZONTAL - GASTOS POR CATEGORIA MÊS FILTRADO
    const coresCategorias = [
        "#06C1AF", // Teal
        "#027385", // Teal escuro
        "#6A11A9", // Roxo
        "#28A745", // Verde
        "#DC3545", // Vermelho
        "#F59E0B", // Amarelo
        "#2563EB", // Azul
        "#64C9C4"  // Turquesa claro
    ];
    const labelsCategoria = dashboard.label_gastos_categoria;
    const data_gastos_categoria = dashboard.data_gastos_categoria;
    const dataGastosCategoria = {
    labels: labelsCategoria,

    datasets: [{
        label: "Gastos por categoria",
        data: data_gastos_categoria,

        backgroundColor: coresCategorias,

        borderWidth: 0,
        borderRadius: 6,

        // HOVER
        hoverBackgroundColor: coresCategorias,
        hoverBorderColor: "#000E32",
        hoverBorderWidth: 2,
        hoverBorderRadius: 8
    }]
};
    const configGastosCategoria = {
        type: 'bar',
        data: dataGastosCategoria,
        options: {
            indexAxis: 'y',
            scales: {
            y: {
                beginAtZero: true
            }
            }
        },
    };
    new Chart(
        document.getElementById("gastosCategoria"),
        configGastosCategoria
    );


    // GRÁFICO DE PIZZA - GASTOS POR FORMA DE PAGAMENTO NO MÊS FILTRADO
    const coresPagamento = [
        "#06C1AF",
        "#6A11A9",
        "#027385",
        "#2563EB",
        "#DC3545",
        "#F59E0B"
    ];
    const labelsFormaPagamento = dashboard.label_gastos_forma_pagamento;
    const data_gastos_forma_pagamento = dashboard.data_gastos_forma_pagamento
    const dataGastosFormaPagamento = {
        labels: labelsFormaPagamento,
        datasets: [{
            label: "Total",
            data: data_gastos_forma_pagamento,

            backgroundColor: coresPagamento,

            borderColor: "#FFFFFF",
            borderWidth: 2,

            hoverOffset: 25
        }]
    };

    const configGastosFormaPagamento = {
        type: 'pie',
        data: dataGastosFormaPagamento,
        options: {
            plugins: {
                legend: {
                    position: 'right',
                    align: 'center'
                }
            }
        }
    };
    new Chart(
        document.getElementById("gastosFormaPagamento"),
        configGastosFormaPagamento
    );
}
catch (error) {
    console.log(error)
}

// FILTROS DASHOBARD 
const selectMes = document.querySelector("#mes_dashboard")
const selectAno = document.querySelector("#ano_dashboard");
const anoAtual = new Date().getFullYear();


const meses = [
    { valor: "01", nome: "JAN" },
    { valor: "02", nome: "FEV" },
    { valor: "03", nome: "MAR" },
    { valor: "04", nome: "ABR" },
    { valor: "05", nome: "MAI" },
    { valor: "06", nome: "JUN" },
    { valor: "07", nome: "JUL" },
    { valor: "08", nome: "AGO" },
    { valor: "09", nome: "SET" },
    { valor: "10", nome: "OUT" },
    { valor: "11", nome: "NOV" },
    { valor: "12", nome: "DEZ" }
];

meses.forEach(mes => {
    const option = document.createElement("option");

    option.value = mes.valor;
    option.text = mes.nome

    if (mes.valor === String(mesSelecionado).padStart(2, "0")) {
        option.selected = true;
    }

    selectMes.appendChild(option)
})

for (let ano = 2022; ano <= anoAtual + 4; ano++) {
    const option = document.createElement("option");
    option.value = ano;
    option.textContent = ano;

    if (String(ano) === String(anoSelecionado)) {
        option.selected = true;
    }
    selectAno.appendChild(option);
}
