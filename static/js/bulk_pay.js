/* MalipoHub — bulk payment CSV preview */
(function () {
  'use strict';

  var input = document.querySelector('input[name="csv_file"]');
  if (!input) return;

  var preview = document.getElementById('csv-preview');
  if (!preview) {
    preview = document.createElement('div');
    preview.id = 'csv-preview';
    preview.className = 'mt-4 text-sm text-brand-muted';
    input.parentNode.appendChild(preview);
  }

  input.addEventListener('change', function () {
    var file = input.files && input.files[0];
    if (!file) { preview.textContent = ''; return; }
    preview.textContent = 'Selected: ' + file.name + ' (' + Math.round(file.size / 1024) + ' KB)';
  });
})();