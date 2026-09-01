const API_URL = 'http://127.0.0.1:8000';
const USER_ID = 1;

const state = {
  categorias: [],
  movimientos: [],
  resumen: null,
  prediccion: null,
  anomalias: [],
  charts: {},
};

document.addEventListener('DOMContentLoaded', async () => {
  bindNav();
  bindModal();
  bindFilters();
  await initDashboard();
});

function bindNav() {
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
      document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
      button.classList.add('active');
      const target = button.dataset.view;
      document.getElementById(target)?.classList.add('active');
    });
  });
}

function bindModal() {
  const modal = document.getElementById('modal-backdrop');
  const openBtn = document.getElementById('new-movement-btn');
  const closeBtn = document.getElementById('close-modal');
  const cancelBtn = document.getElementById('cancel-movement');

  openBtn.addEventListener('click', () => modal.classList.remove('hidden'));
  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (event) => {
    if (event.target === modal) modal.classList.add('hidden');
  });

  const form = document.getElementById('movement-form');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      id_usuario: USER_ID,
      id_categoria: Number(document.getElementById('categoria').value),
      tipo: document.getElementById('tipo').value,
      monto: Number(document.getElementById('monto').value),
      fecha: document.getElementById('fecha').value,
      descripcion: document.getElementById('descripcion').value || '',
    };

    try {
      const res = await fetch(`${API_URL}/api/movimientos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error(result.detail || 'No se pudo guardar el movimiento');
      }

      form.reset();
      modal.classList.add('hidden');
      await initDashboard();
    } catch (error) {
      alert(error.message);
    }
  });
}

function bindFilters() {
  document.getElementById('apply-filters').addEventListener('click', async () => {
    await loadMovimientos();
  });

  document.getElementById('refresh-data').addEventListener('click', async () => {
    await initDashboard();
  });
}

async function initDashboard() {
  await Promise.all([
    loadCategorias(),
    loadResumen(),
    loadPrediccion(),
    loadAnomalias(),
    loadMovimientos(),
  ]);
  renderCharts();
}

async function loadCategorias() {
  const res = await fetch(`${API_URL}/api/categorias?id_usuario=${USER_ID}`);
  const payload = await res.json();
  state.categorias = payload.data || [];

  const categoriaSelect = document.getElementById('categoria');
  const filterCategoria = document.getElementById('filter-categoria');

  const options = state.categorias.map((item) => `
    <option value="${item.id_categoria}">${item.nombre}</option>
  `).join('');

  categoriaSelect.innerHTML = options;
  filterCategoria.innerHTML = `<option value="">Todas las categorías</option>${options}`;
}

async function loadResumen() {
  const res = await fetch(`${API_URL}/api/resumen?id_usuario=${USER_ID}`);
  const payload = await res.json();
  const data = payload.data || {};
  state.resumen = data;

  document.getElementById('total-ingresos').textContent = formatCurrency(data.total_ingresos || 0);
  document.getElementById('total-gastos').textContent = formatCurrency(data.total_gastos || 0);
  document.getElementById('total-balance').textContent = formatCurrency(data.balance || 0);
  document.getElementById('ahorro-neto').textContent = formatCurrency(data.balance || 0);
  document.getElementById('ahorro-porcentaje').textContent = `${Math.max(0, data.ahorro_porcentaje || 0)}%`;

  const status = (data.balance || 0) >= 0 ? 'Estable' : 'Requiere atención';
  const statusText = (data.balance || 0) >= 0
    ? 'Tu flujo financiero está bajo control.'
    : 'Hay más gastos que ingresos en este periodo.';
  document.getElementById('status-label').textContent = status;
  document.getElementById('status-text').textContent = statusText;
}

async function loadPrediccion() {
  const res = await fetch(`${API_URL}/api/analitica/prediccion?id_usuario=${USER_ID}`);
  const payload = await res.json();
  const data = payload.data || {};
  state.prediccion = data;

  document.getElementById('prediccion-mes').textContent = formatCurrency(data.prediccion || 0);
  document.getElementById('gasto-maximo').textContent = formatCurrency(data.prediccion || 0);
}

async function loadAnomalias() {
  const res = await fetch(`${API_URL}/api/analitica/anomalias?id_usuario=${USER_ID}`);
  const payload = await res.json();
  state.anomalias = payload.data || [];

  const alertsContainer = document.getElementById('alerts-container');
  if (state.anomalias.length === 0) {
    alertsContainer.innerHTML = '<p>No se detectaron anomalías.</p>';
    return;
  }

  alertsContainer.innerHTML = state.anomalias.map((item) => `
    <div class="alert-item">
      <strong>${item.categoria}</strong><br>
      Movimiento inusual de ${formatCurrency(item.monto)} el ${item.fecha}<br>
      <small>Z-score: ${item.z_score}</small>
    </div>
  `).join('');

  const insightsList = document.getElementById('insights-list');
  insightsList.innerHTML = state.anomalias.slice(0, 3).map((item) => `
    <li>Se detectó un gasto atípico en ${item.categoria}: ${formatCurrency(item.monto)}.</li>
  `).join('');
}

async function loadMovimientos() {
  const desde = document.getElementById('filter-desde').value;
  const hasta = document.getElementById('filter-hasta').value;
  const categoria = document.getElementById('filter-categoria').value;

  const params = new URLSearchParams({ id_usuario: USER_ID });
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);
  if (categoria) params.append('categoria', categoria);

  const res = await fetch(`${API_URL}/api/movimientos?${params.toString()}`);
  const payload = await res.json();
  state.movimientos = payload.data || [];

  const tableBody = document.getElementById('movimientos-table-body');
  if (!state.movimientos.length) {
    tableBody.innerHTML = '<tr><td colspan="6" class="empty-state">No hay movimientos para este filtro.</td></tr>';
    return;
  }

  tableBody.innerHTML = state.movimientos.map((item) => `
    <tr>
      <td>${item.fecha}</td>
      <td>${item.categoria}</td>
      <td><span class="badge ${item.tipo === 'ingreso' ? 'income' : 'expense'}">${item.tipo}</span></td>
      <td>${item.descripcion || 'Sin descripción'}</td>
      <td class="${item.tipo === 'ingreso' ? 'text-income' : 'text-expense'}">${item.tipo === 'ingreso' ? '+' : '-'}${formatCurrency(item.monto)}</td>
      <td>
        <button class="ghost-btn" data-delete-id="${item.id_movimiento}">Eliminar</button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('[data-delete-id]').forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.dataset.deleteId;
      const resp = await fetch(`${API_URL}/api/movimientos/${id}?id_usuario=${USER_ID}`, {
        method: 'DELETE',
      });

      if (resp.ok) {
        await initDashboard();
      }
    });
  });
}

function renderCharts() {
  if (!state.categorias.length) return;

  const gastosPorCategoria = buildCategoryChartData();
  const tendencia = buildTrendChartData();

  if (state.charts.categoria) state.charts.categoria.destroy();
  if (state.charts.tendencia) state.charts.tendencia.destroy();

  const categoriaCtx = document.getElementById('chart-categorias').getContext('2d');
  state.charts.categoria = new Chart(categoriaCtx, {
    type: 'doughnut',
    data: {
      labels: gastosPorCategoria.labels,
      datasets: [{
        data: gastosPorCategoria.values,
        backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316'],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
    },
  });

  const trendCtx = document.getElementById('chart-tendencia').getContext('2d');
  state.charts.tendencia = new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: tendencia.labels,
      datasets: [
        { label: 'Ingresos', data: tendencia.ingresos, borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', tension: 0.3, fill: false },
        { label: 'Gastos', data: tendencia.gastos, borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.08)', tension: 0.3, fill: false },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: false } },
    },
  });
}

function buildCategoryChartData() {
  const gastos = state.movimientos.filter(item => item.tipo === 'gasto');
  const map = new Map();

  for (const item of gastos) {
    map.set(item.categoria, (map.get(item.categoria) || 0) + Number(item.monto));
  }

  const labels = [...map.keys()];
  const values = [...map.values()];
  return { labels, values };
}

function buildTrendChartData() {
  const months = ['2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08'];
  const ingresos = months.map((month) => {
    const total = state.movimientos
      .filter((item) => item.tipo === 'ingreso' && item.fecha.startsWith(month.slice(0, 4) + '-' + month.slice(5, 7)))
      .reduce((a, b) => a + Number(b.monto), 0);
    return total;
  });

  const gastos = months.map((month) => {
    const total = state.movimientos
      .filter((item) => item.tipo === 'gasto' && item.fecha.startsWith(month.slice(0, 4) + '-' + month.slice(5, 7)))
      .reduce((a, b) => a + Number(b.monto), 0);
    return total;
  });

  return {
    labels: months.map((month) => month.replace('-', '/')),
    ingresos,
    gastos,
  };
}

function formatCurrency(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}
