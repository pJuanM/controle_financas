console.log("Oláaaaa")

const dashboard = window.dashboard;

// GRÁFICO DE LINHA - CUSTOS POR DIA - BASEADO NO MÊS (VENCIMENTO JULHO - COMPRAS QUE VENCE EM JULHO PORÉM COM DATA DE COMPRA DE OUTROS MESES)
const labelsGastosDia = dashboard.label_gastos_dia;
const data_gastos_dia = dashboard.data_gastos_dia;
const dataGastosDia = {
    labels: labelsGastosDia,
    datasets: [{
        label: "Gastos por dia",
        data: data_gastos_dia,
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1
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
            label: 'Gastos por mês',
            data: data_gastos_mes,
            backgroundColor: 'rgba(239, 68, 68, 0.4)',
            borderColor: 'rgb(220, 38, 38)',
            borderWidth: 1
        },
        {
            label: 'Créditos por mês',
            data: data_creditos_mes,  
            backgroundColor: 'rgba(34, 197, 94, 0.4)',
            borderColor: 'rgb(22, 163, 74)',
            borderWidth: 1
        },
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
const labelsCategoria = dashboard.labels_gastos_categoria;
const data_gastos_categoria = dashboard.data_gastos_categoria
const dataGastosCategoria = {
    labels: labelsCategoria,
    datasets: [{
        label: '',
        data: data_gastos_categoria,
        backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)'
        ],
        hoverOffset: 4
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
const labelsFormaPagamento = dashboard.label_gastos_forma_pagamento;
const data_gastos_forma_pagamento = dashboard.data_gastos_forma_pagamento
const dataGastosFormaPagamento = {
    labels: labelsFormaPagamento,
    datasets: [{
        label: 'Total',
        data: data_gastos_forma_pagamento,
        backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)'
        ],
        hoverOffset: 4
    }]
};

const configGastosFormaPagamento = {
    type: 'pie',
    data: dataGastosFormaPagamento,
};
new Chart(
    document.getElementById("gastosFormaPagamento"),
    configGastosFormaPagamento
);
