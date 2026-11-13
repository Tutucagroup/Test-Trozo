/* Krika: filtros laterales y orden en colección y búsqueda (sin recargar la página) */
(function () {
  'use strict';
  if (window.knFacetsReady) return; window.knFacetsReady = true;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  function debounce(fn, ms) { var t; return function () { var a = arguments, s = this; clearTimeout(t); t = setTimeout(function () { fn.apply(s, a); }, ms); }; }
  function isDesk() { return window.matchMedia('(min-width: 990px)').matches; }
  function closePanels() {
    $$('.kn-drawer.is-open').forEach(function (d) { d.classList.remove('is-open'); });
    var o = $('[data-kn-overlay]'); if (o) o.classList.remove('is-open');
    document.documentElement.classList.remove('kn-lock');
  }
  function plpUrl(form) {
    var fd = new FormData(form), p = new URLSearchParams();
    fd.forEach(function (v, k) { if (String(v).trim() !== '') p.append(k, v); });
    var q = p.toString();
    return form.getAttribute('action') + (q ? '?' + q : '');
  }
  function renderPLP(url, push) {
    var plp = $('[data-plp]'); if (!plp) { location.href = url; return; }
    var res = $('[data-results]', plp); if (res) res.classList.add('is-loading');
    var open = $$('.kn-facet', plp).map(function (d) { return d.open; });
    var finds = $$('[data-facet-find]', plp).map(function (i) { return i.value; });
    var focused = document.activeElement && plp.contains(document.activeElement) ? document.activeElement : null;
    var fKey = focused ? (focused.name || '') + '|' + (focused.value || '') + '|' + (focused.id || '') : '';
    var fetchUrl = url + (url.indexOf('?') > -1 ? '&' : '?') + 'section_id=' + encodeURIComponent(plp.dataset.section);
    fetch(fetchUrl).then(function (r) { if (!r.ok) throw 0; return r.text(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var fresh = $('[data-plp]', doc); if (!fresh) throw 0;
      closePanels();
      plp.innerHTML = fresh.innerHTML;
      var det = $$('.kn-facet', plp);
      if (isDesk()) det.forEach(function (d, k) { if (typeof open[k] === 'boolean') d.open = open[k]; });
      $$('[data-facet-find]', plp).forEach(function (i, k) { if (finds[k]) { i.value = finds[k]; i.dispatchEvent(new Event('input', { bubbles: true })); } });
      if (push) history.pushState({ knPlp: 1 }, '', url);
      if (window.KN && window.KN.hydrate) window.KN.hydrate(plp);
      if (fKey) {
        var el = $$('input,select', plp).filter(function (n) { return (n.name || '') + '|' + (n.value || '') + '|' + (n.id || '') === fKey; })[0];
        if (el && isDesk()) try { el.focus({ preventScroll: true }); } catch (e) {}
      }
      var top = plp.getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--kn-hdr-h'), 10) || 140) - 10;
      if (window.scrollY > top) window.scrollTo({ top: top, behavior: 'smooth' });
    }).catch(function () { location.href = url; });
  }
  function init() {
    if (!$('[data-plp]')) return;
    var submitSoon = debounce(function (form) { renderPLP(plpUrl(form), true); }, 650);
    document.addEventListener('submit', function (e) {
      var form = e.target.closest('form[data-facets]'); if (!form) return;
      e.preventDefault(); renderPLP(plpUrl(form), true);
    });
    document.addEventListener('change', function (e) {
      var t = e.target;
      if (t.matches('[data-sort]')) {
        var fid = t.getAttribute('form'), f = fid && document.getElementById(fid);
        if (f && f.hasAttribute('data-facets')) renderPLP(plpUrl(f), true);
        else if (f) { f.appendChild(Object.assign(document.createElement('input'), { type: 'hidden', name: 'sort_by', value: t.value })); f.submit(); }
        return;
      }
      if (t.matches('[data-kn-desc]')) { location.href = t.checked ? t.getAttribute('data-kn-desc') : t.getAttribute('data-kn-off'); return; }
      if (t.matches('[data-kn-newest]')) {
        var sel = $('[data-sort]'), ff = t.closest('form[data-facets]');
        if (sel) sel.value = t.checked ? 'created-descending' : (sel.getAttribute('data-default') || sel.options[0].value);
        if (ff && isDesk()) renderPLP(plpUrl(ff), true);
        return;
      }
      var form = t.closest('form[data-facets]');
      if (!form || t.matches('[data-facet-find]') || !isDesk()) return;
      if (t.matches('[data-price]')) submitSoon(form); else renderPLP(plpUrl(form), true);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && e.target.matches && e.target.matches('[data-facet-find]')) e.preventDefault();
    });
    document.addEventListener('click', function (e) {
      var a = e.target.closest('[data-plp] [data-facet-link], [data-plp] .kn-pag a');
      if (!a || e.metaKey || e.ctrlKey) return;
      e.preventDefault(); renderPLP(a.href, true);
    });
    document.addEventListener('input', function (e) {
      var i = e.target.closest && e.target.closest('[data-facet-find]'); if (!i) return;
      var norm = function (t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
      var q = norm(i.value.trim()), body = i.closest('.kn-facet__body') || i.parentElement;
      $$('[data-facet-item]', body).forEach(function (li) { li.hidden = q !== '' && norm(li.dataset.facetItem).indexOf(q) === -1; });
    });
    window.addEventListener('popstate', function () { if ($('[data-plp]')) renderPLP(location.href, false); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
