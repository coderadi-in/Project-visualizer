// notifications.js — with theme-aware expand/collapse icons

const notificationSection = document.querySelector('.notifications');
const notificationBody = document.querySelector('.notifications .body');
const toggleBtn = document.getElementById('notification-toggle');
const toggleIcon = toggleBtn ? toggleBtn.querySelector('img.icon') : null;

const theme = document.body.classList.contains('dark')? 'dark' : 'light';

// Helper to set toggle icon
function setToggleIcon(isOpen) {
  if (!toggleIcon) return;
  const basePath = `/static/assets/icons/${theme}`;
  toggleIcon.src = isOpen ? `${basePath}/collapse.png` : `${basePath}/expand.png`;
  toggleIcon.alt = isOpen ? 'Collapse section' : 'Expand section';
}

// Initial icon state
setToggleIcon(false);

const socket = io();

// IntersectionObserver to mark notifications as seen
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const id = el.dataset.notificationId || el.id || el.dataset.id;
      const numeric = parseInt(id);
      if (socket) socket.emit('notification-seen', numeric);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.notifications .notification').forEach((el) => observer.observe(el));

// Toggle notifications section
function toggleNotificationsSection(e) {
  if (e) { e.preventDefault && e.preventDefault(); e.stopPropagation && e.stopPropagation(); }
  if (!notificationSection || !notificationBody) return;

  const opening = !notificationSection.classList.contains('open');
  notificationSection.classList.toggle('open', opening);

  setToggleIcon(opening); // update icon

  if (opening) {
    notificationBody.style.display = 'flex';
    requestAnimationFrame(() => {
      notificationBody.style.height = notificationBody.scrollHeight + 'px';
      notificationBody.style.opacity = '1';
    });
  } else {
    notificationBody.style.height = notificationBody.scrollHeight + 'px';
    requestAnimationFrame(() => {
      notificationBody.style.height = '0px';
      notificationBody.style.opacity = '0';
      setTimeout(() => {
        notificationBody.style.display = 'none';
      }, 220);
    });
  }
}

if (toggleBtn) toggleBtn.addEventListener('click', toggleNotificationsSection);

// Close when clicking outside
document.addEventListener('click', (e) => {
  if (!notificationSection) return;
  if (!notificationSection.contains(e.target) && notificationSection.classList.contains('open')) {
    toggleNotificationsSection();
  }
});