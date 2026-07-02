'use strict';

/* =========================================================================
   Galeria de Personagens · mad — vanilla JS, zero deps
   ========================================================================= */

const IMG_BASE = '../'; // gallery/ is served; images live at ../characters/...
const BATCH = 60;

/* ---- Facet definitions: which item field each facet filters on ---- */
const FACETS = [
  { key: 'category',  field: 'role_category', label: 'Categoria', src: 'categories' },
  { key: 'family',    field: 'family',        label: 'Família',   src: 'families'   },
  { key: 'role',      field: 'role_id',       label: 'Role',      src: 'roles'      }, // [id, name]
  { key: 'aesthetic', field: 'aesthetic',     label: 'Estética',  src: 'aesthetics' },
  { key: 'analogy',   field: 'analogy',       label: 'Analogia',  src: 'analogies'  },
];

const state = {
  all: [],
  facets: null,
  filtered: [],
  search: '',
  sel: { category: new Set(), family: new Set(), role: new Set(), aesthetic: new Set(), analogy: new Set() },
  rendered: 0,
  roleName: new Map(), // role_id -> name
};

/* ---- DOM refs ---- */
const $ = (id) => document.getElementById(id);
const grid = $('grid');
const sentinel = $('sentinel');
const emptyEl = $('empty');
const countNum = $('countNum');
const searchInput = $('search');
const searchClear = $('searchClear');
const facetBar = $('facetBar');
const clearAllBtn = $('clearAll');
const activePills = $('activePills');
const popover = $('popover');

/* =========================================================================
   Boot
   ========================================================================= */
init();

async function init() {
  try {
    const [g, f] = await Promise.all([
      fetch('gallery.json').then((r) => r.json()),
      fetch('facets.json').then((r) => r.json()),
    ]);
    state.all = g;
    state.facets = f;
    (f.roles || []).forEach(([id, name]) => state.roleName.set(id, name));
  } catch (err) {
    grid.innerHTML = `<p style="color:var(--text-dim);padding:40px">Falha ao carregar dados: ${err}</p>`;
    return;
  }

  buildFacetButtons();
  wireEvents();
  applyFilters();
}

/* =========================================================================
   Facet buttons
   ========================================================================= */
function buildFacetButtons() {
  facetBar.innerHTML = '';
  for (const f of FACETS) {
    const btn = document.createElement('button');
    btn.className = 'facet-btn';
    btn.dataset.facet = f.key;
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-haspopup', 'true');
    btn.innerHTML = `<span>${f.label}</span>
      <span class="badge" hidden>0</span>
      <svg class="chev" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    btn.addEventListener('click', (e) => { e.stopPropagation(); togglePopover(f, btn); });
    facetBar.appendChild(btn);
  }
}

function refreshFacetButtons() {
  for (const f of FACETS) {
    const btn = facetBar.querySelector(`[data-facet="${f.key}"]`);
    const n = state.sel[f.key].size;
    const badge = btn.querySelector('.badge');
    btn.classList.toggle('has-active', n > 0);
    if (n > 0) { badge.hidden = false; badge.textContent = n; } else { badge.hidden = true; }
  }
}

/* =========================================================================
   Popover (searchable multi-select with faceted counts)
   ========================================================================= */
let openFacet = null;

function optionsFor(f) {
  const src = state.facets[f.src] || [];
  if (f.key === 'role') return src.map(([id, name]) => ({ value: id, label: name }));
  return src.map((v) => ({ value: v, label: v }));
}

// counts for a facet, respecting search + all OTHER active facets
function countsFor(f) {
  const counts = new Map();
  const others = FACETS.filter((x) => x.key !== f.key);
  const q = state.search;
  for (const it of state.all) {
    if (q && !matchText(it, q)) continue;
    let ok = true;
    for (const o of others) {
      const sel = state.sel[o.key];
      if (sel.size && !sel.has(it[o.field])) { ok = false; break; }
    }
    if (!ok) continue;
    const v = it[f.field];
    counts.set(v, (counts.get(v) || 0) + 1);
  }
  return counts;
}

function togglePopover(f, btn) {
  if (openFacet === f.key) { closePopover(); return; }
  openPopover(f, btn);
}

function openPopover(f, btn) {
  closePopover();
  openFacet = f.key;
  btn.setAttribute('aria-expanded', 'true');

  const opts = optionsFor(f);
  const counts = countsFor(f);
  const sel = state.sel[f.key];

  popover.innerHTML = `
    <div class="popover__search">
      <input type="text" placeholder="Filtrar ${f.label.toLowerCase()}…" aria-label="Filtrar opções">
    </div>
    <div class="popover__list" role="listbox" aria-multiselectable="true"></div>
    <div class="popover__foot"><span class="cnt"></span><button type="button" class="clr">Limpar</button></div>`;
  popover.hidden = false;

  const list = popover.querySelector('.popover__list');
  const foot = popover.querySelector('.cnt');
  const search = popover.querySelector('.popover__search input');

  const renderList = (q = '') => {
    const nq = norm(q);
    const rows = opts
      .map((o) => ({ ...o, count: counts.get(o.value) || 0 }))
      .filter((o) => !nq || norm(o.label).includes(nq))
      .sort((a, b) => (sel.has(b.value) - sel.has(a.value)) || b.count - a.count || a.label.localeCompare(b.label));
    if (!rows.length) { list.innerHTML = `<div class="popover__empty">Nada encontrado</div>`; return; }
    list.innerHTML = rows.map((o) => `
      <button class="popover__opt ${o.count === 0 && !sel.has(o.value) ? 'is-zero' : ''}" role="option"
        aria-checked="${sel.has(o.value)}" data-value="${escAttr(o.value)}">
        <span class="check"><svg viewBox="0 0 14 14" width="11" height="11" aria-hidden="true"><path d="M2 7.5l3 3 7-7.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        <span class="lbl">${escHtml(o.label)}</span>
        <span class="cnt">${o.count.toLocaleString('pt-BR')}</span>
      </button>`).join('');
  };

  const updFoot = () => { foot.textContent = sel.size ? `${sel.size} selecionada${sel.size > 1 ? 's' : ''}` : 'Nenhuma'; };

  renderList();
  updFoot();

  list.addEventListener('click', (e) => {
    const opt = e.target.closest('.popover__opt');
    if (!opt) return;
    const v = opt.dataset.value;
    if (sel.has(v)) sel.delete(v); else sel.add(v);
    opt.setAttribute('aria-checked', sel.has(v));
    updFoot();
    refreshFacetButtons();
    renderPills();
    applyFilters();
  });

  search.addEventListener('input', () => renderList(search.value));
  popover.querySelector('.clr').addEventListener('click', () => {
    sel.clear();
    renderList(search.value);
    updFoot(); refreshFacetButtons(); renderPills(); applyFilters();
  });

  positionPopover(btn);
  requestAnimationFrame(() => search.focus());
}

function positionPopover(btn) {
  const r = btn.getBoundingClientRect();
  popover.style.visibility = 'hidden';
  popover.hidden = false;
  const pw = popover.offsetWidth || 300;
  let left = r.left;
  if (left + pw > window.innerWidth - 12) left = window.innerWidth - pw - 12;
  left = Math.max(12, left);
  popover.style.left = `${left}px`;
  popover.style.top = `${r.bottom + 8}px`;
  popover.style.visibility = 'visible';
}

function closePopover() {
  if (openFacet == null) return;
  const btn = facetBar.querySelector(`[data-facet="${openFacet}"]`);
  if (btn) btn.setAttribute('aria-expanded', 'false');
  popover.hidden = true;
  popover.innerHTML = '';
  openFacet = null;
}

/* =========================================================================
   Active pills
   ========================================================================= */
function renderPills() {
  const pills = [];
  for (const f of FACETS) {
    for (const v of state.sel[f.key]) {
      const label = f.key === 'role' ? (state.roleName.get(v) || v) : v;
      pills.push(`<span class="pill"><span class="pill__type">${f.label}</span>${escHtml(label)}
        <button data-facet="${f.key}" data-value="${escAttr(v)}" aria-label="Remover ${escAttr(label)}">&times;</button></span>`);
    }
  }
  if (!pills.length) { activePills.hidden = true; activePills.innerHTML = ''; return; }
  activePills.hidden = false;
  activePills.innerHTML = pills.join('');
  activePills.querySelectorAll('button').forEach((b) => {
    b.addEventListener('click', () => {
      state.sel[b.dataset.facet].delete(b.dataset.value);
      refreshFacetButtons(); renderPills(); applyFilters();
      if (openFacet) closePopover();
    });
  });
}

/* =========================================================================
   Filtering
   ========================================================================= */
function norm(s) { return (s || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
function matchText(it, q) { return norm(it.character_name).includes(q) || norm(it.role_name).includes(q); }

function applyFilters() {
  const q = norm(state.search);
  const active = FACETS.filter((f) => state.sel[f.key].size);
  const out = [];
  for (const it of state.all) {
    if (q && !matchText(it, q)) continue;
    let ok = true;
    for (const f of active) { if (!state.sel[f.key].has(it[f.field])) { ok = false; break; } }
    if (ok) out.push(it);
  }
  state.filtered = out;

  animateCount(out.length);
  const hasFilters = active.length > 0 || state.search;
  clearAllBtn.hidden = !hasFilters;

  renderReset();
}

/* =========================================================================
   Grid render — incremental batches
   ========================================================================= */
function renderReset() {
  grid.innerHTML = '';
  state.rendered = 0;
  emptyEl.hidden = state.filtered.length > 0;
  grid.hidden = state.filtered.length === 0;
  renderMore();
  // if viewport not filled, keep loading
  requestAnimationFrame(fillViewport);
}

function fillViewport() {
  if (state.rendered < state.filtered.length &&
      document.body.scrollHeight <= window.innerHeight + 200) {
    renderMore();
    requestAnimationFrame(fillViewport);
  }
}

function renderMore() {
  const start = state.rendered;
  const end = Math.min(start + BATCH, state.filtered.length);
  if (start >= end) return;
  const frag = document.createDocumentFragment();
  for (let i = start; i < end; i++) frag.appendChild(makeCard(state.filtered[i], i));
  grid.appendChild(frag);
  state.rendered = end;
}

function makeCard(it, index) {
  const btn = document.createElement('button');
  btn.className = 'card';
  btn.type = 'button';
  btn.setAttribute('role', 'listitem');
  btn.dataset.index = index;
  btn.setAttribute('aria-label', `${it.character_name} — ${it.role_name}`);

  const thumb = document.createElement('div');
  thumb.className = 'card__thumb';
  const img = document.createElement('img');
  img.className = 'card__img';
  img.loading = 'lazy';
  img.decoding = 'async';
  img.alt = `${it.character_name} — ${it.role_name}`;
  img.src = IMG_BASE + it.img;
  img.addEventListener('load', () => img.classList.add('loaded'), { once: true });
  img.addEventListener('error', () => { img.style.opacity = '.2'; }, { once: true });
  thumb.appendChild(img);

  const meta = document.createElement('div');
  meta.className = 'card__meta';
  meta.innerHTML = `<div class="card__name">${escHtml(it.character_name)}</div>
    <div class="card__role">${escHtml(it.role_name)}</div>`;

  btn.appendChild(thumb);
  btn.appendChild(meta);
  btn.addEventListener('click', () => openModal(index));
  return btn;
}

/* infinite scroll */
const io = new IntersectionObserver((entries) => {
  if (entries.some((e) => e.isIntersecting)) renderMore();
}, { rootMargin: '600px 0px' });
io.observe(sentinel);

/* =========================================================================
   Animated counter
   ========================================================================= */
let countRAF = null;
function animateCount(target) {
  cancelAnimationFrame(countRAF);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const start = parseInt(countNum.textContent.replace(/\D/g, ''), 10) || 0;
  if (reduce || start === target) { countNum.textContent = target.toLocaleString('pt-BR'); return; }
  const dur = 420, t0 = performance.now();
  const step = (t) => {
    const p = Math.min(1, (t - t0) / dur);
    const e = 1 - Math.pow(1 - p, 3);
    countNum.textContent = Math.round(start + (target - start) * e).toLocaleString('pt-BR');
    if (p < 1) countRAF = requestAnimationFrame(step);
  };
  countRAF = requestAnimationFrame(step);
}

/* =========================================================================
   Modal / detail
   ========================================================================= */
let modalIndex = -1;
let lastFocus = null;
const modal = $('modal');

function openModal(index) {
  modalIndex = index;
  lastFocus = document.activeElement;
  fillModal();
  modal.hidden = false;
  document.body.style.overflow = 'hidden';
  $('mPrev').focus();
}

function fillModal() {
  const it = state.filtered[modalIndex];
  if (!it) return;
  const img = $('mImg');
  img.style.animation = 'none'; void img.offsetWidth; img.style.animation = '';
  img.src = IMG_BASE + it.img;
  img.alt = `${it.character_name} — ${it.role_name}`;
  $('mCategory').textContent = it.role_category || '—';
  $('mName').textContent = it.character_name;
  $('mRole').textContent = it.role_name;
  $('mAesthetic').textContent = it.aesthetic || '—';
  $('mAnalogy').textContent = it.analogy || '—';
  $('mFamily').textContent = it.family || '—';
  $('mSheet').textContent = it.sheet_id || '—';
  $('mId').textContent = it.char_id || '—';
  $('mCounter').textContent = `${(modalIndex + 1).toLocaleString('pt-BR')} de ${state.filtered.length.toLocaleString('pt-BR')}`;
  $('mPrev').disabled = modalIndex <= 0;
  $('mNext').disabled = modalIndex >= state.filtered.length - 1;
}

function navModal(delta) {
  const next = modalIndex + delta;
  if (next < 0 || next >= state.filtered.length) return;
  modalIndex = next;
  fillModal();
}

function closeModal() {
  modal.hidden = true;
  document.body.style.overflow = '';
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}

/* =========================================================================
   Events
   ========================================================================= */
function wireEvents() {
  // search (debounced)
  let sTimer = null;
  searchInput.addEventListener('input', () => {
    searchClear.hidden = !searchInput.value;
    clearTimeout(sTimer);
    sTimer = setTimeout(() => { state.search = searchInput.value.trim(); applyFilters(); }, 120);
  });
  searchClear.addEventListener('click', () => {
    searchInput.value = ''; state.search = ''; searchClear.hidden = true; searchInput.focus(); applyFilters();
  });

  // background toggle
  document.querySelectorAll('.segmented__btn').forEach((b) => {
    b.addEventListener('click', () => {
      document.body.dataset.cardbg = b.dataset.bg;
      document.querySelectorAll('.segmented__btn').forEach((x) => x.setAttribute('aria-pressed', x === b));
    });
  });

  // clear all
  const clearAll = () => {
    state.search = ''; searchInput.value = ''; searchClear.hidden = true;
    FACETS.forEach((f) => state.sel[f.key].clear());
    refreshFacetButtons(); renderPills(); closePopover(); applyFilters();
  };
  clearAllBtn.addEventListener('click', clearAll);
  $('emptyClear').addEventListener('click', clearAll);

  // modal controls
  modal.addEventListener('click', (e) => { if (e.target.dataset.close !== undefined) closeModal(); });
  $('mPrev').addEventListener('click', () => navModal(-1));
  $('mNext').addEventListener('click', () => navModal(1));

  // close popover on outside click / scroll / resize
  document.addEventListener('click', (e) => {
    if (openFacet && !popover.contains(e.target) && !e.target.closest('.facet-btn')) closePopover();
  });
  window.addEventListener('resize', () => { if (openFacet) closePopover(); });
  window.addEventListener('scroll', () => { if (openFacet) closePopover(); }, { passive: true });

  // keyboard
  document.addEventListener('keydown', (e) => {
    if (!modal.hidden) {
      if (e.key === 'Escape') closeModal();
      else if (e.key === 'ArrowLeft') navModal(-1);
      else if (e.key === 'ArrowRight') navModal(1);
      return;
    }
    if (e.key === 'Escape' && openFacet) closePopover();
    if (e.key === '/' && document.activeElement !== searchInput) { e.preventDefault(); searchInput.focus(); }
  });
}

/* =========================================================================
   Utils
   ========================================================================= */
function escHtml(s) {
  return (s == null ? '' : String(s)).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function escAttr(s) { return escHtml(s); }
