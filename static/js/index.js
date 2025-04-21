    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    const placeholderHints = [
      "Ask me anything...",
      "Need a song recommendation?",
      "How are you feeling today?",
      "Got a tech question?",
      "What's on your mind?"
    ];
    let hintIndex = 0;
    setInterval(() => {
      userInput.setAttribute("placeholder", placeholderHints[hintIndex]);
      hintIndex = (hintIndex + 1) % placeholderHints.length;
    }, 4000);

    sendBtn.addEventListener('click', () => {
      const message = userInput.value.trim();
      if (!message) return;

      chatBox.innerHTML += `
        <div class="chat-message user-message">
          <p>${message}</p>
        </div>
      `;
      chatBox.scrollTop = chatBox.scrollHeight;
      userInput.value = '';

      const typingIndicator = document.createElement('div');
      typingIndicator.classList.add('chat-message', 'bot-message');
      typingIndicator.innerHTML = `
        <p class="typing"><span></span><span></span><span></span></p>
      `;
      chatBox.appendChild(typingIndicator);
      chatBox.scrollTop = chatBox.scrollHeight;

        fetch('/prompt', {
        method: 'POST',
         credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: message })

      })
      .then(response => response.json())
      .then(data => {
        typingIndicator.remove();
        chatBox.innerHTML += `
          <div class="chat-message bot-message">
            <p>${data.data}</p>
          </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
      });
    });

    userInput.addEventListener('keypress', e => {
      if (e.key === 'Enter') sendBtn.click();
    });

