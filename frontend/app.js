const API = window.API_URL;
let nivel = "todos";

const $ = (id) => document.getElementById(id);
const FILTRO_LABEL = { todos: "todos", warn: "WARN", critico: "CRÍTICO", normal: "normales" };

function mostrarMensaje(texto, esError = false) {
  const el = $("mensaje");
  el.textContent = texto;
  el.className = esError ? "error" : "";
  el.hidden = !texto;
}

async function pedirJSON(url, opciones) {
  let resp;
  try {
    resp = await fetch(url, opciones);
  } catch {
    throw new Error("No se pudo conectar con el servidor. ¿Está corriendo el backend?");
  }
  const datos = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(datos.error || `Error ${resp.status}`);
  return datos;
}

function celda(tr, texto, clase) {
  const td = document.createElement("td");
  td.textContent = texto;
  if (clase) td.className = clase;
  tr.appendChild(td);
  return td;
}

// -1 = tecnología no disponible
const tec = (tr, v) => (v < 0 ? celda(tr, "N/D", "nd") : celda(tr, v));

function formatearFecha(iso) {
  return iso.replace("T", " ");
}

function pintarTabla(alarmas) {
  const cuerpo = $("cuerpo");
  const frag = document.createDocumentFragment();
  for (const a of alarmas) {
    const tr = document.createElement("tr");
    tr.className = a.nivel.toLowerCase();
    celda(tr, a.id_alarma);
    tec(tr, a.g2); tec(tr, a.g3); tec(tr, a.g4);
    celda(tr, formatearFecha(a.fecha_creacion));
    celda(tr, a.municipio);
    celda(tr, a.departamento);
    celda(tr, a.notificada);
    celda(tr, a.duracion);
    const td = document.createElement("td");
    const b = document.createElement("span");
    b.className = `badge ${a.nivel.toLowerCase()}`;
    b.textContent = a.nivel === "CRITICO" ? "CRÍTICO" : a.nivel === "WARN" ? "WARN" : "Normal";
    td.appendChild(b);
    tr.appendChild(td);
    frag.appendChild(tr);
  }
  cuerpo.replaceChildren(frag);
  $("vacio").hidden = alarmas.length > 0;
}

async function cargar() {
  try {
    const d = await pedirJSON(`${API}/api/alarmas?nivel=${nivel}`);
    pintarTabla(d.alarmas);
    for (const btn of document.querySelectorAll("#filtros [data-nivel]")) {
      btn.querySelector(".n").textContent = d.conteos[btn.dataset.nivel];
    }
    $("pie").textContent = `Mostrando ${d.total} de ${d.conteos.todos} alarmas (${FILTRO_LABEL[nivel]}).`;
  } catch (e) {
    mostrarMensaje(e.message, true);
  }
}

// ---- Filtros
$("filtros").addEventListener("click", (ev) => {
  const btn = ev.target.closest("[data-nivel]");
  if (!btn) return;
  nivel = btn.dataset.nivel;
  document.querySelectorAll("#filtros [data-nivel]").forEach((b) => b.classList.toggle("activo", b === btn));
  cargar();
});
$("btn-refrescar").addEventListener("click", cargar);

// ---- Importar
$("archivo").addEventListener("change", async (ev) => {
  const archivo = ev.target.files[0];
  if (!archivo) return;
  const form = new FormData();
  form.append("archivo", archivo);
  try {
    const r = await pedirJSON(`${API}/api/alarmas/importar`, { method: "POST", body: form });
    let msg = `Importación lista: ${r.nuevas} nuevas, ${r.actualizadas} actualizadas`;
    if (r.rechazadas) msg += `, ${r.rechazadas} filas rechazadas (ej.: línea ${r.errores[0].linea}: ${r.errores[0].error})`;
    mostrarMensaje(msg + ".", r.rechazadas > 0);
    await cargar();
  } catch (e) {
    mostrarMensaje(`No se pudo importar: ${e.message}`, true);
  } finally {
    ev.target.value = "";
  }
});

// ---- Exportar (el backend aplica el mismo filtro que la tabla)
$("btn-exportar").addEventListener("click", () => {
  window.location.href = `${API}/api/alarmas/exportar?nivel=${nivel}`;
});

// ---- Resumen del día
$("btn-resumen").addEventListener("click", async () => {
  const cuerpo = $("resumen-cuerpo");
  cuerpo.textContent = "Cargando…";
  $("modal-resumen").showModal();
  try {
    const r = await pedirJSON(`${API}/api/resumen`);
    const lista = r.por_hora || [];
    const frag = document.createDocumentFragment();
    const titulo = document.createElement("p");
    titulo.textContent = `${r.fecha} — ${r.total} alarmas creadas hoy`;
    frag.appendChild(titulo);
    if (!lista.length) {
      const p = document.createElement("p");
      p.className = "nd";
      p.textContent = "No hay alarmas creadas hoy.";
      frag.appendChild(p);
    }
    const max = Math.max(1, ...lista.map((x) => x.total));
    for (const x of lista) {
      const fila = document.createElement("div");
      fila.className = "barra";
      const h = document.createElement("span"); h.textContent = x.hora;
      const pista = document.createElement("div"); pista.className = "pista";
      const rel = document.createElement("div"); rel.className = "relleno";
      rel.style.width = `${(x.total / max) * 100}%`;
      pista.appendChild(rel);
      const n = document.createElement("span"); n.className = "num"; n.textContent = x.total;
      fila.append(h, pista, n);
      frag.appendChild(fila);
    }
    cuerpo.replaceChildren(frag);
  } catch (e) {
    cuerpo.textContent = e.message;
  }
});

cargar();
