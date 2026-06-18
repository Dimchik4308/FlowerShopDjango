 document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
      });
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
      });
    });

    // Scroll reveal
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animation = 'fadeUp .7s ease both';
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.15 });

    document.querySelectorAll('.product-card, .service-card, .review-card, .feature-item')
      .forEach(el => observer.observe(el));

     const modal = document.getElementById('orderModal');
    const openTriggers = document.querySelectorAll('#openModalTop, #openModalBanner, .open-modal');
    const closeBtn = document.getElementById('closeModal');

    openTriggers.forEach(btn => {
      btn.addEventListener('click', () => modal.classList.add('open'));
    });
    closeBtn.addEventListener('click', () => modal.classList.remove('open'));
    modal.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('open'); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') modal.classList.remove('open'); });

    // Aside filter interaction
    document.querySelectorAll('.aside-item').forEach(item => {
      item.addEventListener('click', () => {
        const list = item.closest('.aside-list');
        list.querySelectorAll('.aside-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });

    // Color swatches
    document.querySelectorAll('.color-swatch').forEach(sw => {
      sw.addEventListener('click', () => sw.classList.toggle('active'));
    });

    // View toggle
    const grid = document.getElementById('productGrid');
    document.querySelectorAll('.view-btn').forEach((btn, i) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        grid.classList.toggle('two-col', i === 1);
      });
    });

    // Pagination
    document.querySelectorAll('.page-btn:not(.arrow)').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.page-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    // Aside filter interaction
    document.querySelectorAll('.aside-item').forEach(item => {
      item.addEventListener('click', () => {
        const section = item.closest('.aside-list');
        section.querySelectorAll('.aside-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });

    // Color swatches
    document.querySelectorAll('.color-swatch').forEach(sw => {
      sw.addEventListener('click', () => sw.classList.toggle('active'));
    });

    // View toggle
    const grid = document.getElementById('productGrid');
    document.querySelectorAll('.view-btn').forEach((btn, i) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        grid.classList.toggle('two-col', i === 1);
      });
    });

    // Pagination
    document.querySelectorAll('.page-btn:not(.arrow)').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.page-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
const mainEmoji = document.getElementById('mainEmoji');
    document.querySelectorAll('.thumb').forEach(t => {
      t.addEventListener('click', () => {
        document.querySelectorAll('.thumb').forEach(x => x.classList.remove('active'));
        t.classList.add('active');
        mainEmoji.textContent = t.dataset.emoji;
        mainEmoji.style.animation = 'none';
        requestAnimationFrame(() => { mainEmoji.style.animation = 'fadeIn .3s ease'; });
      });
    });

    // ── Size selector ──
    const sizeLabel = document.getElementById('sizeLabel');
    const priceMain = document.querySelector('.price-main');
    const stickyPrice = document.getElementById('stickyPrice');
    document.querySelectorAll('.size-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        sizeLabel.textContent = btn.dataset.label;
        const p = btn.dataset.price;
        priceMain.textContent = p;
        stickyPrice.textContent = p + ' грн';
      });
    });

    // ── Color selector ──
    const colorLabel = document.getElementById('colorLabel');
    document.querySelectorAll('.color-opt').forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll('.color-opt').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        colorLabel.textContent = opt.dataset.label;
      });
    });

    // ── Qty ──
    const qtyNum = document.getElementById('qtyNum');
    document.getElementById('qtyMinus').addEventListener('click', () => {
      if (+qtyNum.value > 1) qtyNum.value--;
    });
    document.getElementById('qtyPlus').addEventListener('click', () => {
      if (+qtyNum.value < 99) qtyNum.value++;
    });

    // ── Wishlist ──
    const wishBtn = document.getElementById('wishBtn');
    wishBtn.addEventListener('click', () => {
      const active = wishBtn.classList.toggle('active');
      wishBtn.textContent = active ? '❤️' : '🤍';
    });

    // ── Tabs ──
    document.querySelectorAll('.tab-nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-nav-btn').forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected','false'); });
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        btn.setAttribute('aria-selected','true');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
      });
    });

    function updateButtons() {
    let currentValue = parseInt(inputNum.value);
    let max = parseInt(inputNum.getAttribute('max')) || 99;
    let min = parseInt(inputNum.getAttribute('min')) || 1;

    // Якщо дійшли до мінімуму - вимикаємо мінус
    btnMinus.disabled = currentValue <= min;

    // Якщо дійшли до максимуму - вимикаємо плюс
    btnPlus.disabled = currentValue >= max;
}

// Викликаємо перевірку одразу при завантаженні
updateButtons();

btnPlus.addEventListener('click', function() {
    // ... твій код збільшення ...
    updateButtons(); // Оновлюємо стан кнопок
});

btnMinus.addEventListener('click', function() {
    // ... твій код зменшення ...
    updateButtons(); // Оновлюємо стан кнопок
});