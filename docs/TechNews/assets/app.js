// 科技日报 - 前端交互
(function () {
  'use strict';

  // 搜索过滤
  function initSearch() {
    const input = document.getElementById('search-input');
    if (!input) return;
    input.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.card').forEach(function (card) {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }

  // 回到顶部
  function initBackToTop() {
    const btn = document.createElement('button');
    btn.id = 'back-to-top';
    btn.textContent = '↑';
    btn.title = '回到顶部';
    btn.style.cssText = [
      'position:fixed', 'bottom:2rem', 'right:2rem',
      'width:44px', 'height:44px', 'border-radius:50%',
      'background:#4f8ef7', 'color:#fff', 'border:none',
      'font-size:1.2rem', 'cursor:pointer', 'opacity:0',
      'transition:opacity 0.3s', 'z-index:999',
      'box-shadow:0 4px 12px rgba(79,142,247,0.4)'
    ].join(';');
    document.body.appendChild(btn);

    window.addEventListener('scroll', function () {
      btn.style.opacity = window.scrollY > 400 ? '1' : '0';
    });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initSearch();
    initBackToTop();
  });
})();
