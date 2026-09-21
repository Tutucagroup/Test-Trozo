/* Krika — comportamiento del tema: carruseles, menú móvil, cantidades y carrito */
(function () {
  'use strict';

  /* ------------------------------------------------------------------ *
   * Carrusel por desplazamiento de pista (hero, vitrinas, marcas, UGC)
   * ------------------------------------------------------------------ */
  function Carousel(root) {
    this.root = root;
    this.track = root.querySelector('[data-carousel-track]');
    if (!this.track) return;
    this.slides = Array.prototype.slice.call(this.track.children);
    this.prev = root.querySelector('[data-carousel-prev]');
    this.next = root.querySelector('[data-carousel-next]');
    this.dotsWrap = root.querySelector('[data-carousel-dots]');
    this.index = 0;
    this.loop = root.dataset.loop === 'true';
    this.autoplay = parseInt(root.dataset.autoplay || '0', 10);
    this.build();
  }

  Carousel.prototype.perView = function () {
    if (!this.slides.length) return 1;
    var slideWidth = this.slides[0].getBoundingClientRect().width;
    if (!slideWidth) return 1;
    return Math.max(1, Math.round(this.track.parentElement.getBoundingClientRect().width / slideWidth));
  };

  Carousel.prototype.maxIndex = function () {
    return Math.max(0, this.slides.length - this.perView());
  };

  Carousel.prototype.build = function () {
    var self = this;
    if (this.prev) this.prev.addEventListener('click', function () { self.go(self.index - 1); });
    if (this.next) this.next.addEventListener('click', function () { self.go(self.index + 1); });

    if (this.dotsWrap) this.renderDots();

    var startX = null;
    this.track.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    this.track.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) self.go(self.index + (dx < 0 ? 1 : -1));
      startX = null;
    });

    window.addEventListener('resize', debounce(function () { self.go(self.index, true); }, 150));
    this.go(0, true);

    if (this.autoplay > 0) {
      this.timer = setInterval(function () { self.go(self.index + 1); }, this.autoplay);
      this.root.addEventListener('mouseenter', function () { clearInterval(self.timer); });
      this.root.addEventListener('mouseleave', function () {
        self.timer = setInterval(function () { self.go(self.index + 1); }, self.autoplay);
      });
    }
  };

  Carousel.prototype.renderDots = function () {
    var self = this;
    var count = this.maxIndex() + 1;
    this.dotsWrap.innerHTML = '';
    if (count < 2) return;
    for (var i = 0; i < count; i++) {
      (function (i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'k-carousel__dot';
        b.setAttribute('aria-label', 'Ir a la diapositiva ' + (i + 1));
        b.addEventListener('click', function () { self.go(i); });
        self.dotsWrap.appendChild(b);
      })(i);
    }
  };

  Carousel.prototype.go = function (i, silent) {
    var max = this.maxIndex();
    if (i < 0) i = this.loop ? max : 0;
    if (i > max) i = this.loop ? 0 : max;
    this.index = i;

    var offset = this.slides[i] ? this.slides[i].offsetLeft : 0;
    this.track.style.transform = 'translate3d(' + -offset + 'px,0,0)';

    if (this.dotsWrap) {
      if (silent) this.renderDots();
      Array.prototype.forEach.call(this.dotsWrap.children, function (d, n) {
        d.setAttribute('aria-current', n === i ? 'true' : 'false');
      });
    }
    if (!this.loop) {
      if (this.prev) this.prev.disabled = i <= 0;
      if (this.next) this.next.disabled = i >= max;
    }
  };

  function debounce(fn, wait) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, wait);
    };
  }

  /* ------------------------------------------------------------------ *
   * Barra de anuncios
   * ------------------------------------------------------------------ */
  function initAnnounce(root) {
    var track = root.querySelector('[data-announce-track]');
    if (!track) return;
    var slides = track.children;
    if (slides.length < 2) {
      var nav = root.querySelectorAll('[data-announce-prev],[data-announce-next]');
      Array.prototype.forEach.call(nav, function (n) { n.style.display = 'none'; });
      return;
    }
    var dots = root.querySelector('[data-announce-dots]');
    var i = 0;
    var speed = parseInt(root.dataset.speed || '5000', 10);

    if (dots) {
      for (var n = 0; n < slides.length; n++) {
        (function (n) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'k-announce__dot';
          b.setAttribute('aria-label', 'Anuncio ' + (n + 1));
          b.addEventListener('click', function () { show(n); });
          dots.appendChild(b);
        })(n);
      }
    }

    function show(n) {
      i = (n + slides.length) % slides.length;
      track.style.transform = 'translate3d(' + -(i * 100) + '%,0,0)';
      if (dots) {
        Array.prototype.forEach.call(dots.children, function (d, k) {
          d.setAttribute('aria-current', k === i ? 'true' : 'false');
        });
      }
    }

    var prev = root.querySelector('[data-announce-prev]');
    var next = root.querySelector('[data-announce-next]');
    if (prev) prev.addEventListener('click', function () { show(i - 1); });
    if (next) next.addEventListener('click', function () { show(i + 1); });

    show(0);
    if (speed > 0) {
      var timer = setInterval(function () { show(i + 1); }, speed);
      root.addEventListener('mouseenter', function () { clearInterval(timer); });
      root.addEventListener('mouseleave', function () { timer = setInterval(function () { show(i + 1); }, speed); });
    }
  }

  /* ------------------------------------------------------------------ *
   * Menú móvil
   * ------------------------------------------------------------------ */
  function initDrawer() {
    var drawer = document.querySelector('[data-mobile-drawer]');
    var overlay = document.querySelector('[data-drawer-overlay]');
    if (!drawer) return;
    function open() { drawer.classList.add('is-open'); if (overlay) overlay.classList.add('is-open'); document.body.style.overflow = 'hidden'; }
    function close() { drawer.classList.remove('is-open'); if (overlay) overlay.classList.remove('is-open'); document.body.style.overflow = ''; }
    document.querySelectorAll('[data-drawer-open]').forEach(function (b) { b.addEventListener('click', open); });
    document.querySelectorAll('[data-drawer-close]').forEach(function (b) { b.addEventListener('click', close); });
    if (overlay) overlay.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  /* ------------------------------------------------------------------ *
   * Selectores de cantidad
   * ------------------------------------------------------------------ */
  function initQty(scope) {
    (scope || document).querySelectorAll('[data-qty]').forEach(function (box) {
      if (box.dataset.qtyReady) return;
      box.dataset.qtyReady = '1';
      var input = box.querySelector('input');
      box.querySelectorAll('[data-qty-step]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var step = parseInt(btn.dataset.qtyStep, 10);
          var min = parseInt(input.min || '1', 10);
          var value = Math.max(min, (parseInt(input.value, 10) || min) + step);
          input.value = value;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      });
    });
  }

  /* ------------------------------------------------------------------ *
   * Añadir a la bolsa (AJAX) y contador del carrito
   * ------------------------------------------------------------------ */
  function updateCartCount(count) {
    document.querySelectorAll('[data-cart-count]').forEach(function (el) {
      el.textContent = count;
      el.hidden = count === 0;
    });
  }

  function initAjaxAdd() {
    document.addEventListener('submit', function (e) {
      var form = e.target.closest('form[data-ajax-add]');
      if (!form) return;
      e.preventDefault();
      var button = form.querySelector('[type=submit]');
      var original = button ? button.innerHTML : '';
      if (button) { button.disabled = true; button.innerHTML = 'Agregando…'; }

      fetch(window.Shopify && window.Shopify.routes ? window.Shopify.routes.root + 'cart/add.js' : '/cart/add.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          items: [{ id: form.querySelector('[name=id]').value, quantity: parseInt((form.querySelector('[name=quantity]') || {}).value || 1, 10) }]
        })
      })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.data.description || res.data.message || 'Error');
          if (button) { button.innerHTML = '¡Agregado!'; }
          return fetch('/cart.js').then(function (r) { return r.json(); });
        })
        .then(function (cart) { if (cart) updateCartCount(cart.item_count); })
        .catch(function (err) { if (button) button.innerHTML = err.message || 'No disponible'; })
        .then(function () {
          setTimeout(function () { if (button) { button.disabled = false; button.innerHTML = original; } }, 1600);
        });
    });
  }

  /* ------------------------------------------------------------------ *
   * UGC: reproducir vídeo al pulsar
   * ------------------------------------------------------------------ */
  function initUgc() {
    document.querySelectorAll('[data-ugc-card]').forEach(function (card) {
      var video = card.querySelector('video');
      if (!video) return;
      card.addEventListener('click', function (e) {
        if (e.target.closest('[data-ugc-cta]')) return;
        e.preventDefault();
        if (video.paused) {
          document.querySelectorAll('[data-ugc-card] video').forEach(function (v) {
            if (v !== video) { v.pause(); v.closest('[data-ugc-card]').classList.remove('is-playing'); }
          });
          video.play();
          card.classList.add('is-playing');
        } else {
          video.pause();
          card.classList.remove('is-playing');
        }
      });
      video.addEventListener('ended', function () { card.classList.remove('is-playing'); });
    });
  }

  /* ------------------------------------------------------------------ *
   * Arranque
   * ------------------------------------------------------------------ */
  function init() {
    document.querySelectorAll('[data-carousel]').forEach(function (el) { new Carousel(el); });
    document.querySelectorAll('[data-announce]').forEach(initAnnounce);
    initDrawer();
    initQty();
    initAjaxAdd();
    initUgc();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  document.addEventListener('shopify:section:load', function (e) {
    e.target.querySelectorAll('[data-carousel]').forEach(function (el) { new Carousel(el); });
    e.target.querySelectorAll('[data-announce]').forEach(initAnnounce);
    initQty(e.target);
    initUgc();
  });
})();
