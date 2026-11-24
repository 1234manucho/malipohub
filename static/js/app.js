/* MalipoHub — global JS */
(function () {
  'use strict';

  // Auto-dismiss flash messages after 6s
  document.querySelectorAll('[class*="flash-"]').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s ease';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 6000);
  });

  // Confirm destructive form submits
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!window.confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  // Format number inputs to two decimals on blur
  document.querySelectorAll('input[type="number"][step="0.01"]').forEach(function (input) {
    input.addEventListener('blur', function () {
      if (input.value && !isNaN(parseFloat(input.value))) {
        input.value = parseFloat(input.value).toFixed(2);
      }
    });
  });

  // Mobile nav toggle placeholder (extend if you add a hamburger)
  var toggle = document.getElementById('nav-toggle');
  var menu = document.getElementById('nav-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      menu.classList.toggle('hidden');
    });
  }
})();