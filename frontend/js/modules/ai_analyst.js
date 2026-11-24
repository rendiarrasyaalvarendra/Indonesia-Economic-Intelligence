/**
 * AI Economic Analyst Chatbot Module
 */
function loadAIAnalyst() {
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const chatHistory = [];

  const SUGGESTED_QUESTIONS = [
    'Berapa pertumbuhan PDB Indonesia terbaru?',
    'Bagaimana tren inflasi di Indonesia?',
    'Apa kondisi ketenagakerjaan terbaru?',
    'Bagaimana kinerja neraca perdagangan Indonesia?',
    'Provinsi mana dengan kemiskinan tertinggi?',
  ];

  // Render suggested questions
  document.getElementById('chat-suggestions').innerHTML = SUGGESTED_QUESTIONS.map(q =>
    `<button class="btn btn-ghost btn-sm" onclick="askQuestion('${q}')" style="margin:3px">${q}</button>`
  ).join('');

  // Initial welcome message
  appendMessage('ai', `**Selamat datang di AI Economic Analyst Indonesia!** 🇮🇩

Saya dapat membantu Anda memahami data ekonomi Indonesia berdasarkan data resmi dari **BPS** dan **Bank Indonesia**.

Anda dapat bertanya tentang:
- 📈 Pertumbuhan PDB dan tren ekonomi
- 📊 Inflasi dan Indeks Harga Konsumen  
- 💱 Kurs USD/IDR dan BI Rate
- 👥 Ketenagakerjaan dan kemiskinan
- 🌏 Neraca perdagangan internasional
- 🗺️ Perbandingan ekonomi antar provinsi

Silakan ketik pertanyaan Anda!`);

  window.askQuestion = function (q) {
    chatInput.value = q;
    sendMessage();
  };

  async function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;

    chatInput.value = '';
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    appendMessage('user', msg);
    chatHistory.push({ role: 'user', content: msg });

    // Typing indicator
    const typingId = appendTyping();

    let result;
    try {
      result = await window.API.chat(msg, chatHistory.slice(-10));
    } catch (e) {
      removeTyping(typingId);
      appendMessage('ai', `⚠️ Maaf, terjadi kesalahan: ${e.message}`);
      chatInput.disabled = false;
      chatSendBtn.disabled = false;
      chatInput.focus();
      return;
    }

    removeTyping(typingId);
    appendMessage('ai', result.reply, result.sources);
    chatHistory.push({ role: 'assistant', content: result.reply });

    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    chatInput.focus();
  }

  function appendMessage(role, content, sources = []) {
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = `chat-avatar ${role}`;
    avatar.textContent = role === 'ai' ? '🤖' : '👤';

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    // Render markdown-like bold
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    bubble.innerHTML = formatted;

    if (sources.length > 0) {
      const src = document.createElement('div');
      src.className = 'chat-sources';
      src.innerHTML = '📚 ' + sources.map(s => `<span class="badge badge-blue">${s}</span>`).join(' ');
      bubble.appendChild(src);
    }

    div.appendChild(avatar);
    div.appendChild(bubble);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div.id;
  }

  function appendTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'chat-message ai';
    div.id = id;
    div.innerHTML = `
      <div class="chat-avatar ai">🤖</div>
      <div class="chat-bubble ai">
        <span class="spinner" style="display:inline-block;margin-right:8px"></span> Menganalisis data...
      </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  chatSendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

window.ModuleAIAnalyst = { loadAIAnalyst };
