// Selección de elementos del DOM
const inputMensaje = document.getElementById('mensaje');
const btnEnviar = document.getElementById('enviar');
const divRespuesta = document.getElementById('respuesta');

// Inicializar Marked.js options para que maneje line breaks
if (typeof marked !== 'undefined') {
  marked.setOptions({
    breaks: true,
    gfm: true
  });
}

function appendUserMessage(text) {
  const html = `
        <div class="message user">
            <div class="avatar user-avatar">U</div>
            <div class="bubble">
                <div class="content">${text}</div>
            </div>
        </div>
    `;
  divRespuesta.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function createAIFutureMessage() {
  // Retorna los objetos DOM necesarios para la actualización en stream
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message ai';

  messageDiv.innerHTML = `
        <div class="avatar ai-avatar">T</div>
        <div class="bubble">
            <div class="content cursor-pulso"></div>
        </div>
    `;

  divRespuesta.appendChild(messageDiv);
  scrollToBottom();

  return messageDiv.querySelector('.content');
}

function scrollToBottom() {
  setTimeout(() => {
    divRespuesta.parentElement.scrollTop = divRespuesta.parentElement.scrollHeight;
  }, 10);
}

async function sendMessage() {
  const mensaje = inputMensaje.value;

  if (mensaje.trim() === '') {
    return; // No enviar vacío
  }

  appendUserMessage(mensaje);
  inputMensaje.value = '';

  const contentDiv = createAIFutureMessage();
  let accumulatedText = '';

  try {
    const response = await fetch(`/ia/chat/${encodeURIComponent(mensaje)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      contentDiv.classList.remove('cursor-pulso');
      contentDiv.innerHTML = `<p>Hubo un error en la solicitud.</p>`;
      scrollToBottom();
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      accumulatedText += chunk;

      // Usar marked para parsear markdown
      if (typeof marked !== 'undefined') {
        contentDiv.innerHTML = marked.parse(accumulatedText);
      } else {
        // Fallback a texto plano
        contentDiv.textContent = accumulatedText;
      }

      scrollToBottom();
    }

    // Al finalizar remover cursor animado
    contentDiv.classList.remove('cursor-pulso');

  } catch (error) {
    console.error("Error fetching stream:", error);
    contentDiv.classList.remove('cursor-pulso');
    contentDiv.innerHTML = `<p>Error de conexión al servidor.</p>`;
    scrollToBottom();
  }
}

// Evento de click en el botón enviar
btnEnviar.addEventListener('click', sendMessage);

// Evento Enter key
inputMensaje.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendMessage();
  }
});