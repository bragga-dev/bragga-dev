document.addEventListener('DOMContentLoaded', function () {

  const btn = document.getElementById('menu-btn');
  const menu = document.getElementById('mobile-menu');

  if (btn && menu) {
    btn.addEventListener('click', () => {
      menu.classList.toggle('hidden');
    });
  }

  const userBtn = document.getElementById('user-menu-btn');
  const dropdown = document.getElementById('user-dropdown');

  if (userBtn && dropdown) {
    userBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', function (e) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
  }

});