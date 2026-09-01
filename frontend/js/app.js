// ============================================================
// Finance Hub — Frontend (JavaScript vanilla + Chart.js)
// Consumo de la API REST con fetch() / async-await.
// ============================================================

const API_URL = 'http://127.0.0.1:8000';
const STORAGE_KEY = 'finance_hub_user';

// --- Estado global ---
const state = {
  usuario: null,          // { id_usuario, nombre, correo }
  categorias: [],
  movimientos: [],
  resumen: null,
  prediccion: null,
  anomalias: [],
  insights: null,
  charts: {},
  editandoMovimiento: null,   // id del movimiento en edición o null
  editandoCategoria: null,     // id de la categoría en edición o null
};

// --- Utilidades ---
const $ = (id) => document.getElementById(id);

function formatCurrency(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(value ||  0));
}

function formatPercentage(value) {
  return `${Number(value ||  0).toFixed(1)}%`;
}

function showError(el, message) {
  if (!el) return;
  el.textContent = message;
  el.classList.remove('hidden');
}

function hideError(el) {
  if (el) el.classList.add('hidden');
}

async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);
  let payload;
  try {
    payload = await res.json();
  } catch {
    payload = {};
  }
  if (!res.ok) {
    const detail = payload.detail;
    const msg = typeof detail === 'string' ? detail : (detail
      ? (typeof detail[0] === 'string' ? detail[0] : detail[0].msg)
      : `Error ${res.status}`);
    throw new Error(msg);
  }
  return payload;
}

// ============================================================
// AUTENTICACIÓN (RF01)
// ============================================================

function loadSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveSession(usuario) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(usuario));
}

function clearSession() {
  localStorage.removeItem(STORAGE_KEY);
}

function mostrarAuth() {
  $('app-auth').classList.remove('hidden');
  document.querySelector('.app-shell').classList.add('hidden');
}

async function mostrarApp(usuario) {
  state.usuario = usuario;
  saveSession(usuario);
  $('app-auth').classList.add('hidden');
  document.querySelector('.app-shell').classList.remove('hidden');
  $('user-name').textContent = usuario.nombre;
  $('user-email').textContent = usuario.correo;
  await initDashboard();
}

async function cargarUsuariosParaLogin() {
  try {
    const payload = await apiFetch(`${API_URL}/api/usuarios`);
    const usuarios = payload.data || [];;
    const select = $('login-usuario');
    select.innerHTML = '<option value="">Selecciona tu usuario...</option>' +
      usuarios.map((u) =>
        `<option value="${u.id_usuario}" data-nombre="${u.nombre}" data-correo="${u.correo}">${u.nombre} (${u.correo})</option>`
      ).join('');
  } catch (error) {
    $('login-message').textContent = 'No se pudieron cargar los usuarios: ' + error.message;
    $('login-message').classList.add('error');
  }
}

function bindAuth() {
  // Pestañas login/registro
  document.querySelectorAll('.auth-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const target = tab.dataset.authTab === 'register' ? 'register-form' : 'login-form';
      const other = target === 'register-form' ? 'login-form' : 'register-form';
      $(target).classList.remove('hidden');
      $(other).classList.add('hidden');
      hideError($('login-message'));
      hideError($('register-message'));
    });
  });

  // Login (selección de usuario existente)
  $('login-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const select = $('login-usuario');
    const option = select.options[select.selectedIndex];
    if (!option || !option.value) {
      showError($('login-message'), 'Selecciona un usuario.');
      return;
    }
    mostrarApp({
      id_usuario: Number(option.value),
      nombre: option.dataset.nombre,
      correo: option.dataset.correo,
    });
  });

  // Registro de usuario
  $('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const nombre = $('register-nombre').value.trim();
    const correo = $('register-correo').value.trim();
    const contrasena = $('register-contrasena').value;
    hideError($('register-message'));

    if (contrasena.length < 6) {
      showError($('register-message'), 'La contraseña debe tener al menos 6 caracteres.');
      return;
    }

    const btn = event.submitter;
    btn.disabled = true;
    try {
      const payload = await apiFetch(`${API_URL}/api/usuarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, correo, contrasena }),
      });
      mostrarApp(payload.data);
    } catch (error) {
      showError($('register-message'), error.message);
    } finally {
      btn.disabled = false;
    }
  });

  $('logout-btn').addEventListener('click', () => {
    clearSession();
    state.usuario = null;
    state.categorias = [];
    state.movimientos = [];
    state.resumen = null;
    state.prediccion = null;
    state.anomalias = [];
    state.insights = null;
    Object.values(state.charts).forEach((chart) => chart?.destroy());
    state.charts = {};
    mostrarAuth();
    cargarUsuariosParaLogin();
  });
}
// ============================================================
// INICIO DE LA APLICACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
  const usuario = loadSession();
  if (usuario) {
    mostrarApp(usuario);
  } else {
    mostrarAuth();
    await cargarUsuariosParaLogin();
  }
  bindNav();
  bindModal();
  bindCategoryModal();
  bindFilters();
});

function bindNav() {
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
      document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
      button.classList.add('active');
      const target = button.dataset.view;
      document.getElementById(target)?.classList.add('active');
      const titles = {
        overview: 'Tu panel financiero',
        movimientos: 'Movimientos',
        categorias: 'Categorías',
        analitica: 'Analítica avanzada',
      };
      $('topbar-title').textContent = titles[target] || 'Tu panel financiero';
    });
  });

  $('open-categories-btn').addEventListener('click', () => {
    document.querySelector(`.nav-item[data-view="categorias"]`).click();
  });

  $('new-category-btn').addEventListener('click', () => openCategoryModal());
}

// ============================================================
// MODAL DE MOVIMIENTOS (crear/editar + validación JS)
// ============================================================

function bindModal() {
  const modal = $('modal-backdrop');
  const openBtn = $('new-movement-btn');
  const closeBtn = $('close-modal');
  const cancelBtn = $('cancel-movement');

  openBtn.addEventListener('click', () => openMovementModal());
  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (event) => {
    if (event.target === modal) modal.classList.add('hidden');
  });

  // Al cambiar el tipo, se filtran las categorías correspondientes
  $('tipo').addEventListener('change', () => fillCategoriaSelect());

  $('movement-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideError($('movement-form-error'));

    const error = validarMovimientoForm();
    if (error) {
      showError($('movement-form-error'), error);
      return;
    }

    const tipo = $('tipo').value;
    const payload = {
      id_usuario: state.usuario.id_usuario,
      id_categoria: Number($('categoria').value),
      tipo,
      monto: Number($('monto').value),
      fecha: $('fecha').value,
      descripcion: $('descripcion').value.trim() || '',
    };

    const btn = event.submitter;
    btn.disabled = true;
    try {
      const idEditar = state.editandoMovimiento;
      if (idEditar) {
        await apiFetch(`${API_URL}/api/movimientos/${idEditar}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        await apiFetch(`${API_URL}/api/movimientos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }
      modal.classList.add('hidden');
      await initDashboard();
    } catch (error) {
      showError($('movement-form-error'), error.message);
    } finally {
      btn.disabled = false;
    }
  });
}

function fillCategoriaSelect() {
  const tipo = $('tipo').value;
  const select = $('categoria');
  const categoriaActual = select.value;
  const filtradas = state.categorias.filter((c) => c.tipo === tipo);

  if (!filtradas.length) {
    select.innerHTML = '<option value="">No hay categorías de este tipo. Créalas en "Categorías"</option>';
    return;
  }

  select.innerHTML = filtradas.map((c) =>
    `<option value="${c.id_categoria}" ${String(c.id_categoria) === String(categoriaActual) ? 'selected' : ''}>${c.nombre}</option>`
  ).join('');
}

function validarMovimientoForm() {
  const tipo = $('tipo').value;
  const monto = Number($('monto').value);
  const fecha = $('fecha').value;
  const categoria = $('categoria').value;

  if (!$('monto').value.trim() || !Number.isFinite(monto) || monto <= 0) {

    return 'El monto debe ser un número positivo mayor a 0.';
  }

  if (!fecha) {
    return 'La fecha es obligatoria.';
  }



  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  const fechaSel = new Date(fecha + 'T00:00:00');
  if (tipo === 'gasto' && fechaSel > hoy) {

    return 'La fecha de un gasto no puede ser futura.';
  }

        if (!categoria) {
    return 'Selecciona una categoría para el movimiento.';
  }



  const cat = state.categorias.find((c) => String(c.id_categoria) === String(categoria));
  if (!cat || cat.tipo !== tipo) {

    return 'La categoría seleccionada no coincide con el tipo del movimiento.';
  }

        return null;
}

function openMovementModal(movimiento = null) {
  state.editandoMovimiento = movimiento ? movimiento.id_movimiento : null;
  $('movement-modal-title').textContent = movimiento ? 'Editar movimiento' : 'Nuevo movimiento';
  $('movimiento-id').value = movimiento ? movimiento.id_movimiento : '';
  $('tipo').value = movimiento ? movimiento.tipo : 'gasto';
  $('monto').value = movimiento ? movimiento.monto : '';
  $('fecha').value = movimiento ? movimiento.fecha : new Date().toISOString().slice(0, 10);
  $('descripcion').value = movimiento ? (movimiento.descripcion || '') : '';
  hideError($('movement-form-error'));
  fillCategoriaSelect();
  if (movimiento) {
    $('categoria').value = movimiento.id_categoria;
  }
  $('modal-backdrop').classList.remove('hidden');
}
// ============================================================
// MODAL DE CATEGORÍAS (RF02: CRUD completo)
// ============================================================

function bindCategoryModal() {
  const modal = $('modal-categoria-backdrop');
  const closeBtn = $('close-category-modal');
  const cancelBtn = $('cancel-category');

  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (event) => {
    if (event.target === modal) modal.classList.add('hidden');
  });

  $('category-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    hideError($('category-form-error'));

    const nombre = $('category-nombre').value.trim();
    const tipo = $('category-tipo').value;
    if (!nombre) {
      showError($('category-form-error'), 'El nombre de la categoría es obligatorio.');
      return;
    }

    const payload = {
      id_usuario: state.usuario.id_usuario,
      nombre,
      tipo,
    };

    const btn = event.submitter;
    btn.disabled = true;
    try {
      const idEditar = state.editandoCategoria;
      if (idEditar) {
        await apiFetch(`${API_URL}/api/categorias/${idEditar}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        await apiFetch(`${API_URL}/api/categorias`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }
      modal.classList.add('hidden');
      await initDashboard();
    } catch (error) {
      showError($('category-form-error'), error.message);
    } finally {
      btn.disabled = false;
    }
  });
}

function openCategoryModal(categoria = null) {
  state.editandoCategoria = categoria ? categoria.id_categoria : null;
  $('category-modal-title').textContent = categoria ? 'Editar categoría' : 'Nueva categoría';
  $('categoria-id').value = categoria ? categoria.id_categoria : '';
  $('category-nombre').value = categoria ? categoria.nombre : '';
  $('category-tipo').value = categoria ? categoria.tipo : 'gasto';
  hideError($('category-form-error'));
  $('modal-categoria-backdrop').classList.remove('hidden');
}

function renderCategorias() {

  const container = $('categorias-list');

  if (!state.categorias.length) {
    container.innerHTML = '<span class="empty-state">No hay categorías. Crea la primera con "+ Nueva categoría".</span>';
    return;
  }



  container.innerHTML = state.categorias.map((cat) => `
    <span class="badge ${cat.tipo === 'ingreso' ? 'income' : 'expense'}">
      ${cat.nombre}
      <button type="button" class="icon-sm edit" data-edit-cat="${cat.id_categoria}" title="Editar">✎</button>
      <button type="button" class="icon-sm delete" data-delete-cat="${cat.id_categoria}" title="Eliminar">✕</button>
    </span>
  `).join('');

  document.querySelectorAll('[data-edit-cat]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const cat = state.categorias.find((c) => String(c.id_categoria) === btn.dataset.editCat);
      if (cat) openCategoryModal(cat);
    });
  });

  document.querySelectorAll('[data-delete-cat]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.deleteCat;
      if (!confirm('¿Eliminar esta categoría?')) return;
      try {
        await apiFetch(`${API_URL}/api/categorias/${id}?id_usuario=${state.usuario.id_usuario}`, {
          method: 'DELETE',
        });
        await initDashboard();
      } catch (error) {
        alert(error.message);
      }
    });
  });
}
// ============================================================
// ============================================================
// CARGA DEL DASHBOARD (RF03-RF10)
// ============================================================

async function initDashboard() {
  try {
    await Promise.all([
      loadCategorias(),
      loadResumen(),
      loadPrediccion(),
      loadAnomalias(),
      loadMovimientos(),
      loadInsights(),
    ]);
    renderCharts();
    renderCategorias();
  } catch (error) {
    alert('Error al cargar el panel: ' + error.message);
  }
}

async function loadCategorias() {
  const payload = await apiFetch(`${API_URL}/api/categorias?id_usuario=${state.usuario.id_usuario}`);
  state.categorias = payload.data || [];
  const filterCategoria = $('filter-categoria');
  const estadoActual = filterCategoria.value;
  filterCategoria.innerHTML = '<option value="">Todas las categorías</option>' +
    state.categorias.map((c) => `<option value="${c.id_categoria}"${String(c.id_categoria) === String(estadoActual) ? ' selected' : ''}>${c.nombre}</option>`).join('');
}

async function loadResumen() {
  const payload = await apiFetch(`${API_URL}/api/resumen?id_usuario=${state.usuario.id_usuario}`);
  const data = payload.data || {};
  state.resumen = data;
  $('total-ingresos').textContent = formatCurrency(data.total_ingresos ||  0);
  $('total-gastos').textContent = formatCurrency(data.total_gastos ||  0);
  $('total-balance').textContent = formatCurrency(data.balance ||  0);
  $('ahorro-neto').textContent = formatCurrency(data.balance ||  0);
  $('ahorro-porcentaje').textContent = formatPercentage(Math.max(0, data.ahorro_porcentaje ||  0));
  const status = (data.balance ||  0) >=  0 ? 'Estable' : 'Requiere atención';
  const statusText = (data.balance ||  0) >=  0
    ? 'Tu flujo financiero está bajo control.'
    : 'Hay más gastos que ingresos en este periodo.';
  $('status-label').textContent = status;
  $('status-text').textContent = statusText;
}

async function loadPrediccion() {
  const payload = await apiFetch(`${API_URL}/api/analitica/prediccion?id_usuario=${state.usuario.id_usuario}`);
  const data = payload.data || {};
  state.prediccion = data;
  $('prediccion-mes').textContent = formatCurrency(data.prediccion ||  0);
  $('prediccion-razon').textContent = data.razon || (data.mes_estimado ? `Mes estimado: ${data.mes_estimado}` : '');
}

async function loadAnomalias() {
  const payload = await apiFetch(`${API_URL}/api/analitica/anomalias?id_usuario=${state.usuario.id_usuario}`);
  state.anomalias = payload.data || [];
  const alertsContainer = $('alerts-container');
  if (!state.anomalias.length) {
    alertsContainer.innerHTML = '<span class="empty-state">No se detectaron anomalías.</span>';
    return;
  }
  alertsContainer.innerHTML = state.anomalias.map((item) => `
    <div class="alert-item">
      <strong>${item.categoria}</strong><br>
      Movimiento inusual de ${formatCurrency(item.monto)} el ${item.fecha}<br>
      <small>Z-score: ${item.z_score} · Promedio histórico: ${formatCurrency(item.promedio_categoria)}</small>
    </div>
  `).join('');
}

async function loadMovimientos() {
  const desde = $('filter-desde').value;
  const hasta = $('filter-hasta').value;
  const categoria = $('filter-categoria').value;
  const params = new URLSearchParams({ id_usuario: state.usuario.id_usuario });
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);
  if (categoria) params.append('categoria', categoria);
  const payload = await apiFetch(`${API_URL}/api/movimientos?${params.toString()}`);
  state.movimientos = payload.data || [];
  renderMovimientos();
}

async function loadInsights() {
  const payload = await apiFetch(`${API_URL}/api/analitica/insights?id_usuario=${state.usuario.id_usuario}`);
  state.insights = payload.data || {};
  renderInsights();
}

function renderInsights() {
  const insights = state.insights || {};
  const { categoria_mas_costosa_mes, categoria_mas_costosa_historico,tendencia_mensual } = insights;
  const insightsList = $('insights-list');
  const items = [];
  if (categoria_mas_costosa_mes) {
    items.push(`<li>📊 En ${categoria_mas_costosa_mes.mes} la categoría más costosa fue <strong>${categoria_mas_costosa_mes.categoria}</strong> (${formatCurrency(categoria_mas_costosa_mes.total)}).</li>`);
  }
        if (categoria_mas_costosa_historico) {

    items.push(`<li>🏆 Históricamente gastas más en <strong>${categoria_mas_costosa_historico.categoria}</strong> (${formatCurrency(categoria_mas_costosa_historico.total)} en total).</li>`);
  }
        const ultimo = tendencia_mensual?.length ? tendencia_mensual[tendencia_mensual.length - 1] : null;
  if (ultimo) {
    items.push(`<li>💡 En ${ultimo.mes} ahorraste ${formatPercentage(ultimo.ahorro_porcentaje)}de tus ingresos.</li>`);
  }
        if (state.prediccion?.prediccion) {
    items.push(`<li>🔮 Se espera que gastes ${formatCurrency(state.prediccion.prediccion)} el próximo mes (confianza: ${state.prediccion.confianza}).</li>`);
  }
        if (state.anomalias?.length) {
    items.push(`<li>🚨 Se detectaron ${state.anomalias.length} movimiento(s) anómalo(s.</li>`);
  }
        insightsList.innerHTML = items.length ? items.join('') : '<li>Registra movimientos para ver análisis.</li>';
}function renderMovimientos() {
  const tableBody = $('movimientos-table-body');
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
        <button type="button" class="icon-sm edit" data-edit-id="${item.id_movimiento}" title="Editar">✎ Editar</button>
        <button type="button" class="icon-sm delete" data-delete-id="${item.id_movimiento}" title="Eliminar">✕ Eliminar</button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('[data-delete-id]').forEach((button) => {
    button.addEventListener('click', async () => {
      if (!confirm('¿Eliminar este movimiento?')) return;
      try {
        await apiFetch(`${API_URL}/api/movimientos/${button.dataset.deleteId}?id_usuario=${state.usuario.id_usuario}`, {
          method: 'DELETE',
        });
        await initDashboard();
      } catch (error) {
        alert(error.message);
      }
    });
  });

  document.querySelectorAll('[data-edit-id]').forEach((button) => {
    button.addEventListener('click', () => {
      const movimiento = state.movimientos.find((m) => String(m.id_movimiento) === button.dataset.editId);
      if (movimiento) openMovementModal(movimiento);
    });
  });
}

function bindFilters() {
  $('apply-filters').addEventListener('click', async () => {
    await loadMovimientos();
  });
  $('refresh-data').addEventListener('click', async () => {
    await initDashboard();
  });
}

function renderCharts() {
  Object.values(state.charts).forEach((chart) => chart?.destroy());
  state.charts = {};
  const gastosPorCategoria = buildCategoryChartData();
  const tendencia = buildTrendChartData();
  if (gastosPorCategoria.labels.length) {
    const categoriaCtx = $('chart-categorias').getContext('2d');
    state.charts.categoria = new Chart(categoriaCtx, {
      type: 'doughnut',
      data: {
        labels: gastosPorCategoria.labels,
        datasets: [{
          data: gastosPorCategoria.values,
          backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#6366f1', '#22c55e', '#e11d48'],
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }
        if (tendencia.labels.length) {
    const trendCtx = $('chart-tendencia').getContext('2d');
    state.charts.tendencia = new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: tendencia.labels,
        datasets: [
          { label: 'Ingresos', data: tendencia.ingresos, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.3, fill: false },
          { label: 'Gastos', data: tendencia.gastos, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.08)', tension: 0.3, fill: false },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }
}

function buildCategoryChartData() {
  const gastos = state.movimientos.filter((item) => item.tipo === 'gasto');
  const map = new Map();
  for (const item of gastos) {
    map.set(item.categoria,(map.get(item.categoria) ||  0) + Number(item.monto));
  }
        return { labels: [...map.keys()], values: [...map.values()] };
}

function buildTrendChartData() {
  const tendencia = (state.insights && state.insights.tendencia_mensual) || [];
  if (tendencia.length) {
    return {
      labels: tendencia.map((item) => item.mes.replace('-', '/')),
      ingresos: tendencia.map((item) => item.ingresos),
      gastos: tendencia.map((item) => item.gastos),
    };
  }
        const meses = [...new Set(state.movimientos.map((m) => m.fecha.slice(0, 7)))].sort();
  const ingresos = meses.map((mes) =>
    state.movimientos.filter((m) => m.tipo === 'ingreso' && m.fecha.startsWith(mes))
      .reduce((a, b) => a + Number(b.monto), 0)
  );
        const gastos = meses.map((mes) =>
    state.movimientos.filter((m) => m.tipo === 'gasto' && m.fecha.startsWith(mes))
      .reduce((a, b) => a + Number(b.monto), 0)
  );
        return {
    labels: meses.map((mes) => mes.replace('-', '/')),
    ingresos,
    gastos,
  };
}
