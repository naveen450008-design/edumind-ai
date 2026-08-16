/* EduMind AI Main Frontend JS System */

document.addEventListener('DOMContentLoaded', () => {
  console.log('EduMind AI System Initialized.');

  // Theme Switcher Initialization
  const currentTheme = localStorage.getItem('edumind_theme') || 'dark';
  applyTheme(currentTheme);

  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      applyTheme(activeTheme);
      localStorage.setItem('edumind_theme', activeTheme);
    });
  }

  // Mobile Sidebar Toggle
  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }

  // Quick Login Handlers
  const quickLoginBtns = document.querySelectorAll('.quick-login-btn');
  quickLoginBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const role = btn.dataset.role;
      const email = btn.dataset.email;
      const pass = btn.dataset.pass || 'student123';

      const roleSelect = document.getElementById('role');
      const emailInput = document.getElementById('email');
      const passInput = document.getElementById('password');

      if (roleSelect) roleSelect.value = role;
      if (emailInput) emailInput.value = email;
      if (passInput) passInput.value = pass;

      const loginForm = document.getElementById('loginForm');
      if (loginForm) loginForm.submit();
    });
  });
});

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  if (theme === 'light') {
    document.body.classList.add('light-mode');
  } else {
    document.body.classList.remove('light-mode');
  }
  const themeIcon = document.getElementById('themeIcon');
  if (themeIcon) {
    themeIcon.className = theme === 'light' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill text-warning';
  }
}

// AI Chatbot / Copilot Helper Function
function sendChatMessage() {
  const inputEl = document.getElementById('chatInput');
  if (!inputEl) return;
  const question = inputEl.value.trim();
  if (!question) return;

  const chatContainer = document.getElementById('chatMessages');
  if (!chatContainer) return;

  // Append User message
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.textContent = question;
  chatContainer.appendChild(userDiv);

  inputEl.value = '';
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Show typing indicator bot message
  const botDiv = document.createElement('div');
  botDiv.className = 'chat-msg bot';
  botDiv.innerHTML = '<i class="bi bi-cpu spin me-1"></i> Analyzing student data...';
  chatContainer.appendChild(botDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Send API Request to Copilot Chatbot Endpoint
  fetch('/api/copilot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question })
  })
  .then(res => res.json())
  .then(data => {
    botDiv.innerHTML = data.response || 'Sorry, I could not analyze that query at the moment.';
    chatContainer.scrollTop = chatContainer.scrollHeight;
  })
  .catch(err => {
    // Fallback to existing student chat endpoint if copilot chat fails
    fetch('/api/student/ai-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question })
    })
    .then(r => r.json())
    .then(d => {
      botDiv.innerHTML = d.response || 'Sorry, could not process request.';
      chatContainer.scrollTop = chatContainer.scrollHeight;
    })
    .catch(() => {
      botDiv.textContent = 'Error communicating with AI Assistant.';
    });
  });
}

function askQuickQuestion(text) {
  const inputEl = document.getElementById('chatInput');
  if (inputEl) {
    inputEl.value = text;
    sendChatMessage();
  }
}

// Task Toggle Handler for Study Plan
function toggleTask(taskId, isChecked) {
  fetch('/api/student/study-task/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, is_completed: isChecked })
  })
  .then(r => r.json())
  .then(data => {
    if (data.status === 'success') {
      const row = document.getElementById('task-row-' + taskId);
      if (row) {
        if (isChecked) {
          row.classList.add('text-decoration-line-through', 'opacity-50');
        } else {
          row.classList.remove('text-decoration-line-through', 'opacity-50');
        }
      }
    }
  });
}
