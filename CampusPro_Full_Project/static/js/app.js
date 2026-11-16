const toggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
if (toggle && sidebar) toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
document.querySelectorAll('.flash button').forEach(btn => btn.addEventListener('click', () => btn.parentElement.remove()));
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', () => {
  const button = form.querySelector('button[type="submit"],button:not([type])');
  if (button && !form.classList.contains('filter-bar')) { button.dataset.oldText = button.innerHTML; button.innerHTML = '<i class="bi bi-arrow-repeat"></i> Please wait...'; button.disabled = true; }
}));
document.querySelectorAll('.flash').forEach(item => setTimeout(() => { item.classList.add('fade-out'); setTimeout(() => item.remove(), 350); }, 5500));
