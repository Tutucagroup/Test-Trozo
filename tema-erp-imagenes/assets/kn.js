/* Krika — Estilo Natura: carruseles, cabecera, menús, bolsa lateral, favoritos y ficha de producto */
(function () {
  'use strict';
  var root = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  function debounce(fn, ms) { var t; return function () { var a = arguments, s = this; clearTimeout(t); t = setTimeout(function () { fn.apply(s, a); }, ms); }; }

  /* ---------------- Carrusel ---------------- */
  function Carousel(el) {
    if (el._kn) return; el._kn = this;
    this.el = el;
    this.track = $('[data-car-track]', el);
    if (!this.track) return;
    this.prev = $('[data-car-prev]', el);
    this.next = $('[data-car-next]', el);
    this.dots = $('[data-car-dots]', el);
    this.loop = el.dataset.loop === 'true';
    this.auto = parseInt(el.dataset.autoplay || '0', 10);
    this.i = 0;
    var s = this;
    if (this.prev) this.prev.addEventListener('click', function () { s.go(s.i - 1); s.stop(); });
    if (this.next) this.next.addEventListener('click', function () { s.go(s.i + 1); s.stop(); });
    var x0 = null, y0 = null;
    this.track.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    this.track.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) { s.go(s.i + (dx < 0 ? 1 : -1)); s.stop(); }
      x0 = null;
    });
    window.addEventListener('resize', debounce(function () { s.go(s.i, true); }, 150));
    this.go(0, true);
    if (this.auto > 0 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      this.timer = setInterval(function () { s.go(s.i + 1); }, this.auto);
      el.addEventListener('mouseenter', function () { s.stop(); });
    }
  }
  Carousel.prototype.slides = function () { return $$('.kn-car__slide', this.track).filter(function (n) { return n.offsetParent !== null; }); };
  Carousel.prototype.max = function () {
    var sl = this.slides(); if (!sl.length) return 0;
    var vw = this.track.parentElement.getBoundingClientRect().width;
    var total = this.track.scrollWidth;
    if (total <= vw + 2) return 0;
    for (var k = 0; k < sl.length; k++) { if (sl[k].offsetLeft >= total - vw - 2) return k; }
    return sl.length - 1;
  };
  Carousel.prototype.stop = function () { if (this.timer) { clearInterval(this.timer); this.timer = null; } };
  Carousel.prototype.go = function (i, silent) {
    var sl = this.slides(), max = this.max();
    if (i < 0) i = this.loop ? max : 0;
    if (i > max) i = this.loop ? 0 : max;
    this.i = i;
    var vw = this.track.parentElement.getBoundingClientRect().width;
    var off = sl[i] ? sl[i].offsetLeft : 0;
    off = Math.min(off, Math.max(0, this.track.scrollWidth - vw));
    this.track.style.transform = 'translate3d(' + -off + 'px,0,0)';
    sl.forEach(function (n, k) { n.setAttribute('aria-hidden', k < i ? 'true' : 'false'); });
    if (this.dots) {
      if (silent || this.dots.children.length !== max + 1) this.renderDots(max);
      $$('button', this.dots).forEach(function (d, k) { d.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    }
    if (!this.loop) {
      if (this.prev) this.prev.disabled = i <= 0;
      if (this.next) this.next.disabled = i >= max;
    }
  };
  Carousel.prototype.renderDots = function (max) {
    var s = this; this.dots.innerHTML = '';
    if (max < 1) return;
    for (var k = 0; k <= max; k++) (function (k) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'kn-car__dot'; b.setAttribute('aria-label', 'ir al grupo ' + (k + 1));
      b.addEventListener('click', function () { s.go(k); s.stop(); });
      s.dots.appendChild(b);
    })(k);
  };
  function initCarousels(scope) { $$('[data-car]', scope).forEach(function (el) { new Carousel(el); }); }

  /* ---------------- Cabecera ---------------- */
  function initHeader() {
    var hdr = $('[data-kn-header]');
    if (!hdr) return;
    function measure() { document.documentElement.style.setProperty('--kn-hdr-h', hdr.offsetHeight + 'px'); }
    measure(); window.addEventListener('resize', debounce(measure, 100));
    var last = 0;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      hdr.classList.toggle('is-scrolled', y > 20);
      last = y;
    }, { passive: true });

    /* Mega menú: abre al pasar o al enfocar, cierra al salir o con Escape */
    $$('[data-mega-item]', hdr).forEach(function (item) {
      var t;
      function open() { clearTimeout(t); $$('[data-mega-item].is-open', hdr).forEach(function (o) { if (o !== item) o.classList.remove('is-open'); }); item.classList.add('is-open'); var a = $('a', item); if (a) a.setAttribute('aria-expanded', 'true'); }
      function close() { t = setTimeout(function () { item.classList.remove('is-open'); var a = $('a', item); if (a) a.setAttribute('aria-expanded', 'false'); }, 120); }
      item.addEventListener('mouseenter', open);
      item.addEventListener('mouseleave', close);
      item.addEventListener('focusin', open);
      item.addEventListener('focusout', function (e) { if (!item.contains(e.relatedTarget)) close(); });
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('[data-mega-item].is-open').forEach(function (o) { o.classList.remove('is-open'); }); });
  }

  /* ---------------- Paneles laterales ---------------- */
  var overlay;
  function openPanel(p) {
    overlay = overlay || $('[data-kn-overlay]');
    $$('.kn-drawer.is-open').forEach(function (d) { if (d !== p) d.classList.remove('is-open'); });
    p.classList.add('is-open'); if (overlay) overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    var f = $('button, a', p); if (f) setTimeout(function () { f.focus(); }, 50);
  }
  function closePanels() {
    $$('.kn-drawer.is-open').forEach(function (d) { d.classList.remove('is-open'); });
    if (overlay) overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }
  function initPanels() {
    overlay = $('[data-kn-overlay]');
    document.addEventListener('click', function (e) {
      var o = e.target.closest('[data-open-panel]');
      if (o) { var p = document.getElementById(o.getAttribute('data-open-panel')); if (p) { e.preventDefault(); if (p.id === 'KnCart') refreshCart().then(function () { openPanel(p); }); else openPanel(p); } return; }
      if (e.target.closest('[data-close-panel]') || e.target === overlay) closePanels();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanels(); });
  }

  /* ---------------- Cantidades ---------------- */
  function initQty(scope) {
    $$('[data-qty]', scope).forEach(function (box) {
      if (box._kn) return; box._kn = 1;
      var input = $('input', box);
      $$('[data-step]', box).forEach(function (b) {
        b.addEventListener('click', function () {
          var min = parseInt(input.min || '1', 10);
          input.value = Math.max(min, (parseInt(input.value, 10) || min) + parseInt(b.dataset.step, 10));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      });
    });
  }

  /* ---------------- Bolsa ---------------- */
  function setCount(n) { $$('[data-cart-count]').forEach(function (el) { el.textContent = n; el.hidden = n === 0; }); }
  function toast(msg) {
    var t = $('[data-kn-toast]'); if (!t) return;
    t.textContent = msg; t.classList.add('is-visible');
    clearTimeout(t._t); t._t = setTimeout(function () { t.classList.remove('is-visible'); }, 2600);
  }
  function refreshCart() {
    var drawer = document.getElementById('KnCart');
    if (!drawer) return Promise.resolve();
    return fetch(root + '?sections=kn-cart-drawer').then(function (r) { return r.json(); }).then(function (d) {
      var html = new DOMParser().parseFromString(d['kn-cart-drawer'], 'text/html');
      var inner = $('[data-cd-inner]', html);
      if (inner) { $('[data-cd-inner]', drawer).replaceWith(inner); initQty(drawer); }
      var c = $('[data-cd-count]', html); if (c) setCount(parseInt(c.dataset.cdCount, 10) || 0);
    });
  }
  function changeLine(key, qty) {
    var drawer = document.getElementById('KnCart');
    if (drawer) drawer.classList.add('is-loading');
    return fetch(root + 'cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: key, quantity: qty }) })
      .then(function () { return refreshCart(); })
      .then(function () { if (drawer) drawer.classList.remove('is-loading'); });
  }
  /* Imagen del producto como propiedad oculta de la línea (_imagen_url): llega al ERP en el webhook orders/create.
     El guion bajo hace que Shopify no la muestre en el checkout ni en los correos. */
  function imgFor(form, input) {
    var src = input && input.tagName === 'SELECT' ? input.options[input.selectedIndex] : input;
    var v = (src && src.getAttribute('data-img')) || form.getAttribute('data-img') || '';
    return v.trim();
  }
  function lineItem(form, idInput) {
    var item = { id: idInput.value, quantity: parseInt((form.querySelector('[name=quantity]') || {}).value || 1, 10) };
    var img = imgFor(form, idInput);
    if (img) item.properties = { _imagen_url: img };
    return item;
  }
  /* Respaldo: si un formulario no trae la imagen, se toma la de la bolsa y se guarda en la línea. Nunca bloquea la compra. */
  function ensureImg(d) {
    var it = d && d.items && d.items[0];
    if (!it || !it.image || (it.properties && it.properties._imagen_url)) return Promise.resolve();
    return fetch(root + 'cart.js').then(function (r) { return r.json(); }).then(function (cart) {
      var line = (cart.items || []).filter(function (x) { return x.key === it.key; })[0];
      if (!line || (line.properties && line.properties._imagen_url)) return;
      var props = {}, k;
      for (k in (line.properties || {})) props[k] = line.properties[k];
      props._imagen_url = line.image || it.image;
      return fetch(root + 'cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: line.key, quantity: line.quantity, properties: props }) });
    }).catch(function () {});
  }
  function initCart() {
    document.addEventListener('submit', function (e) {
      var form = e.target.closest('form[data-ajax-add]');
      if (!form) return;
      e.preventDefault();
      var btn = $('[type=submit]', form), txt = btn ? btn.innerHTML : '';
      var idInput = form.querySelector('[name=id]:checked') || form.querySelector('[name=id]');
      if (btn) { btn.disabled = true; btn.textContent = 'Agregando…'; }
      fetch(root + 'cart/add.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ items: [lineItem(form, idInput)] })
      }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.d.description || res.d.message || 'No disponible');
          return ensureImg(res.d);
        })
        .then(function () {
          var p = document.getElementById('KnCart');
          return refreshCart().then(function () { if (p && !form.hasAttribute('data-no-drawer')) openPanel(p); else toast('Producto agregado a tu bolsa'); });
        })
        .catch(function (err) { toast(err.message); })
        .then(function () { if (btn) { btn.disabled = false; btn.innerHTML = txt; } });
    });
    document.addEventListener('change', function (e) {
      var i = e.target.closest('[data-line-qty]');
      if (i) changeLine(i.dataset.lineQty, parseInt(i.value, 10) || 0);
    });
    document.addEventListener('click', function (e) {
      var r = e.target.closest('[data-line-remove]');
      if (r) { e.preventDefault(); changeLine(r.dataset.lineRemove, 0); }
    });
  }

  /* ---------------- Favoritos (guardados en este navegador) ---------------- */
  var FAV = 'kn-favs';
  function favs() { try { return JSON.parse(localStorage.getItem(FAV) || '[]'); } catch (e) { return []; } }
  function paintFavs() {
    var f = favs();
    $$('[data-fav]').forEach(function (b) { b.setAttribute('aria-pressed', f.indexOf(b.dataset.fav) > -1 ? 'true' : 'false'); });
    $$('[data-fav-count]').forEach(function (el) { el.textContent = f.length; el.hidden = f.length === 0; });
  }
  function initFavs() {
    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-fav]'); if (!b) return;
      e.preventDefault();
      var f = favs(), h = b.dataset.fav, k = f.indexOf(h);
      if (k > -1) f.splice(k, 1); else f.push(h);
      try { localStorage.setItem(FAV, JSON.stringify(f)); } catch (err) {}
      paintFavs();
      toast(k > -1 ? 'Quitado de favoritos' : 'Guardado en favoritos');
    });
    paintFavs();
    var list = $('[data-fav-list]');
    if (list) {
      var f = favs();
      if (!f.length) return;
      $('[data-fav-empty]') && ($('[data-fav-empty]').hidden = true);
      Promise.all(f.map(function (h) { return fetch(root + 'products/' + h + '?section_id=kn-card-render').then(function (r) { return r.ok ? r.text() : ''; }).catch(function () { return ''; }); }))
        .then(function (arr) { list.innerHTML = arr.join(''); initQty(list); paintFavs(); });
    }
  }

  /* ---------------- Pestañas ---------------- */
  function initTabs(scope) {
    $$('[data-tabs]', scope).forEach(function (box) {
      if (box._kn) return; box._kn = 1;
      box.addEventListener('click', function (e) {
        var t = e.target.closest('[role=tab]'); if (!t) return;
        $$('[role=tab]', box).forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
        $$('[role=tabpanel]', box).forEach(function (p) { p.hidden = p.id !== t.getAttribute('aria-controls'); });
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        var car = panel && $('[data-car]', panel);
        if (car) { if (car._kn) car._kn.go(0, true); else new Carousel(car); }
        var cover = $('[data-tab-cover]', box);
        if (cover && t.dataset.cover) { var img = $('img', cover); if (img) { img.src = t.dataset.cover; img.removeAttribute('srcset'); } cover.href = t.dataset.url || cover.href; }
      });
    });
  }

  /* ---------------- Vídeos ---------------- */
  function initVideos() {
    document.addEventListener('click', function (e) {
      var m = e.target.closest('[data-vid]'); if (!m) return;
      var v = $('video', m); if (!v) return;
      var card = m.closest('.kn-vid');
      if (v.paused) {
        $$('[data-vid] video').forEach(function (o) { if (o !== v) { o.pause(); o.closest('.kn-vid').classList.remove('is-playing'); } });
        v.muted = false; v.play(); card.classList.add('is-playing');
      } else { v.pause(); card.classList.remove('is-playing'); }
    });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (en) {
        en.forEach(function (x) { var v = x.target; if (!x.isIntersecting && !v.paused) { v.pause(); v.closest('.kn-vid').classList.remove('is-playing'); } });
      });
      $$('[data-vid] video').forEach(function (v) { io.observe(v); });
    }
  }

  /* ---------------- Carga diferida de vitrinas (marca, recomendados) ---------------- */
  function initLazy() {
    $$('[data-lazy-src]').forEach(function (box) {
      function load() {
        fetch(box.dataset.lazySrc).then(function (r) { return r.ok ? r.text() : ''; }).then(function (html) {
          var doc = new DOMParser().parseFromString(html, 'text/html');
          var inner = $('[data-lazy-content]', doc);
          if (inner && box.dataset.exclude) $$('[data-fav="' + box.dataset.exclude + '"]', inner).forEach(function (b) { var sl = b.closest('.kn-car__slide'); if (sl) sl.remove(); });
          if (inner && $('.kn-car__slide', inner)) { box.innerHTML = ''; box.appendChild(inner); box.hidden = false; initCarousels(box); initQty(box); paintFavs(); }
          else box.remove();
        }).catch(function () { box.remove(); });
      }
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { io.disconnect(); load(); } }, { rootMargin: '400px' });
        io.observe(box.hidden ? box.parentElement : box);
      } else load();
    });
  }

  /* ---------------- Aparición suave ---------------- */
  function initReveal() {
    if (!('IntersectionObserver' in window)) { $$('.kn-reveal').forEach(function (el) { el.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -60px' });
    $$('.kn-reveal').forEach(function (el) { io.observe(el); });
  }

  /* ---------------- Anuncios ---------------- */
  function initAnnounce() {
    $$('[data-announce]').forEach(function (el) {
      var items = $$('.kn-announce__item', el); if (items.length < 2) return;
      var i = 0;
      setInterval(function () { items[i].classList.remove('is-active'); i = (i + 1) % items.length; items[i].classList.add('is-active'); }, parseInt(el.dataset.speed || '5000', 10));
    });
  }

  function init() {
    initHeader(); initPanels(); initCarousels(); initQty(); initCart(); initFavs(); initTabs(); initVideos(); initLazy(); initReveal(); initAnnounce();
  }
  window.KN = { hydrate: function (s) { initCarousels(s); initQty(s); initTabs(s); paintFavs(); }, openPanel: openPanel, refreshCart: refreshCart, toast: toast };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  document.addEventListener('shopify:section:load', function (e) { window.KN.hydrate(e.target); $$('.kn-reveal', e.target).forEach(function (el) { el.classList.add('is-in'); }); });
})();
