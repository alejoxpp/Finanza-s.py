const API_URL = 'http://127.0.0.1:8000/api';
const USER_ID = 1; // Usuario de prueba

document.addEventListener('DOMContentLoaded', async () => {
    await cargarCategorias();
    await cargarResumen();
    await cargarPrediccion();
    await cargarAnomalias();
    inicializarGraficos();
});

async function cargarResumen() {
    const res = await fetch(`${API_URL}/resumen?id_usuario=${USER_ID}`);
    const data = await res.json();
    document.getElementById('card-ingresos').innerText = `$${data.total_ingresos.toLocaleString()}`;
    document.getElementById('card-gastos').innerText = `$${data.total_gastos.toLocaleString()}`;
    document.getElementById('card-balance').innerText = `$${data.balance.toLocaleString()}`;
}

async function cargarPrediccion() {
    const res = await fetch(`${API_URL}/analitica/prediccion?id_usuario=${USER_ID}`);
    const data = await res.json();
    document.getElementById('card-prediccion').innerText = `$${data.prediccion.toLocaleString()}`;
}

async function cargarAnomalias() {
    const res = await fetch(`${API_URL}/analitica/anomalias?id_usuario=${USER_ID}`);
    const data = await res.json();
    const alertBox = document.getElementById('alerta-anomalias');
    const lista = document.getElementById('lista-anomalias');
    
    if (data.anomalias.length > 0) {
        alertBox.style.display = 'block';
        lista.innerHTML = data.anomalias.map(a => 
            `<li>Gasto inusual el ${a.fecha}: $${a.monto.toLocaleString()} (Promedio categoría: $${a.promedio_categoria.toLocaleString()})</li>`
        ).join('');
    }
}

async function cargarCategorias() {
    const res = await fetch(`${API_URL}/categorias?id_usuario=${USER_ID}`);
    const data = await res.json();
    const select = document.getElementById('categoria');
    select.innerHTML = data.map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
}

function inicializarGraficos() {
    // Gráfico Donut - Gastos por categoría
    const ctxDoughnut = document.getElementById('chartCategorias').getContext('2d');
    new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
            labels: ['Alimentación', 'Transporte', 'Entretenimiento', 'Salud'],
            datasets: [{
                data: [320000, 90000, 150000, 800000],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
            }]
        },
        options: { plugins: { title: { display: true, text: 'Gastos por Categoría' } } }
    });

    // Gráfico Líneas - Tendencia Ingresos vs Gastos
    const ctxLine = document.getElementById('chartTendencia').getContext('2d');
    new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: ['Junio', 'Julio'],
            datasets: [
                { label: 'Ingresos', data: [2500000, 2500000], borderColor: '#2ecc71', fill: false },
                { label: 'Gastos', data: [560000, 1100000], borderColor: '#e74c3c', fill: false }
            ]
        },
        options: { plugins: { title: { display: true, text: 'Tendencia Mensual' } } }
    });
}

// Envío del formulario
document.getElementById('form-movimiento').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        id_usuario: USER_ID,
        id_categoria: parseInt(document.getElementById('categoria').value),
        tipo: document.getElementById('tipo').value,
        monto: parseFloat(document.getElementById('monto').value),
        fecha: document.getElementById('fecha').value,
        descripcion: document.getElementById('descripcion').value
    };

    await fetch(`${API_URL}/movimientos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    location.reload();
});