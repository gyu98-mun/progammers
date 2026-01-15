(() => {
  const track = document.querySelector('.carousel__track');
  const prev = document.querySelector('.carousel__btn--prev');
  const next = document.querySelector('.carousel__btn--next');
  const dotsWrap = document.querySelector('.dots');
  const originalSlides = Array.from(document.querySelectorAll('.carousel__track .slide'));

  if (!track || originalSlides.length === 0) return;

  // settings
  let spv = 2; // slides per view: desktop=2, mobile=1
  let stepPercent = 50; // 100/spv
  let n = originalSlides.length;

  // state (slide index in "cloned" track)
  let index = 0;
  let dots = [];
  let timer = null;

  function computeSPV() {
    spv = window.matchMedia('(max-width: 768px)').matches ? 1 : 2;
    stepPercent = 100 / spv;
  }

  function pagesCount() {
    return Math.ceil(n / spv);
  }

  function buildDots(activePage) {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = '';
    dots = [];
    const pages = pagesCount();
    for (let p = 0; p < pages; p++) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'dot' + (p === activePage ? ' is-active' : '');
      b.setAttribute('aria-label', `${p + 1}번 페이지`);
      b.addEventListener('click', () => goToPage(p));
      dotsWrap.appendChild(b);
      dots.push(b);
    }
  }

  // Clone helpers (for seamless looping)
  function clearClones() {
    Array.from(track.querySelectorAll('[data-clone="1"]')).forEach(el => el.remove());
  }

  function setupClones() {
    clearClones();
    // clone last spv to head
    const headClones = originalSlides.slice(n - spv, n).map(s => s.cloneNode(true));
    headClones.forEach(c => { c.dataset.clone = "1"; track.insertBefore(c, track.firstChild); });

    // clone first spv to tail
    const tailClones = originalSlides.slice(0, spv).map(s => s.cloneNode(true));
    tailClones.forEach(c => { c.dataset.clone = "1"; track.appendChild(c); });
  }

  function setTransition(on) {
    track.style.transition = on ? 'transform .35s ease' : 'none';
  }

  function setIndex(newIndex, withAnim=true) {
    index = newIndex;
    setTransition(withAnim);
    track.style.transform = `translateX(-${index * stepPercent}%)`;
  }

  function pageOfCurrent() {
    // index is in cloned space: [0..spv-1] are head clones, originals start at spv
    const originalIndex = index - spv; // 0..n-1
    const page = Math.floor(originalIndex / spv);
    return Math.max(0, Math.min(pagesCount() - 1, page));
  }

  function updateDots() {
    const p = pageOfCurrent();
    dots.forEach((d, i) => d.classList.toggle('is-active', i === p));
  }

  function go(deltaPages) {
    const deltaSlides = deltaPages * spv; // ✅ 2개 단위 이동(데스크톱), 1개 단위(모바일)
    setIndex(index + deltaSlides, true);
  }

  function goToPage(page) {
    // target original slide index = page*spv, convert to cloned space
    setIndex(spv + page * spv, true);
  }

  function onTransitionEnd() {
    // boundary snap for seamless loop
    // if moved past last originals into tail clones
    if (index >= spv + n) {
      // snap to start originals
      setIndex(spv, false);
    }
    // if moved before first originals into head clones
    if (index < spv) {
      // snap to last page start (in originals)
      const lastStart = spv + (pagesCount() - 1) * spv;
      setIndex(lastStart, false);
    }
    updateDots();
  }

  function restartAuto() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => go(1), 6000);
  }

  function init() {
    computeSPV();
    setupClones();
    // start at first originals page
    setIndex(spv, false);
    buildDots(0);
    updateDots();
    restartAuto();
  }

  // events
  track.addEventListener('transitionend', onTransitionEnd);
  prev?.addEventListener('click', () => { go(-1); restartAuto(); });
  next?.addEventListener('click', () => { go(1); restartAuto(); });

  window.addEventListener('resize', () => init());

  init();
})();
/* =====================================================
   여기저기 - ICONIC MINIMAL behaviors
   ===================================================== */

// 1) Scroll reveal (hero + sections)
(() => {
  const targets = document.querySelectorAll('.hero, .section');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) e.target.classList.add('is-visible');
    });
  }, { threshold: 0.12 });

  targets.forEach(t => io.observe(t));
})();

// 2) Header compact on scroll
(() => {
  const header = document.querySelector('.header');
  if (!header) return;

  const onScroll = () => {
    header.classList.toggle('is-compact', window.scrollY > 8);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// 3) Chip active state (클릭하면 .is-active 토글)
// - 기존에 chip 기능이 이미 있으면, 이 부분은 중복될 수 있음.
// - 중복이면 기존 로직에 classList.toggle('is-active')만 섞어도 됨.
(() => {
  const chips = document.querySelectorAll('.chip');
  if (!chips.length) return;

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('is-active');
    });
  });
})();



// Theme search: Enter or 검색 버튼(submit)으로 필터 적용
(() => {
  const form = document.getElementById('searchForm');
  const input = document.getElementById('themeSearch');
  const cards = Array.from(document.querySelectorAll('#themes .card'));
  if (!input || cards.length === 0) return;

  function applyFilter(){
    const q = input.value.trim().toLowerCase();
    cards.forEach(card => {
      const text = (card.textContent + " " + (card.getAttribute('data-keywords') || "")).toLowerCase();
      card.style.display = q === "" || text.includes(q) ? "" : "none";
    });
  }

  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    applyFilter();
  });

  // UX: 입력값 지우면 자동으로 전체 복구
  input.addEventListener('input', () => {
    if (input.value.trim() === "") applyFilter();
  });
})();


// Search suggestions dropdown
(() => {
  const input = document.getElementById('themeSearch');
  const panel = document.getElementById('suggestions');
  const closeBtn = document.querySelector('.suggestions__close');
  const chipsWrap = document.getElementById('suggestionChips');
  const form = document.getElementById('searchForm');

  if (!input || !panel || !chipsWrap) return;

  function openPanel(){
    panel.hidden = false;
  }
  function closePanel(){
    panel.hidden = true;
  }

  input.addEventListener('focus', openPanel);
  input.addEventListener('click', openPanel);

  closeBtn?.addEventListener('click', closePanel);

  // click outside closes
  document.addEventListener('click', (e) => {
    const target = e.target;
    if (!(target instanceof Element)) return;
    const field = input.closest('.search-field');
    if (!field) return;
    if (!field.contains(target)) closePanel();
  });

  // chip click fills input + triggers search
  chipsWrap.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const text = btn.textContent.replace('#','').trim();
    input.value = text;
    // trigger submit to apply filter
    form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    closePanel();
    input.focus();
  });
})();
