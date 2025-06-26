const form = document.querySelector("#chat-form");
const input = document.querySelector("#user-input");
const chatWindow = document.querySelector(".chat-window");
const scrollBtn = document.querySelector("#scroll-to-bottom");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userMsg = input.value.trim();
  if (!userMsg) return;

  appendMessage("user", userMsg);
  input.value = "";

  appendMessage("bot", `<div class="dot-typing"><span></span></div>`);

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: userMsg }),
  });

  const data = await res.json();
  const botMsg = data.response || "Xin lỗi, hệ thống đang gặp lỗi.";

  await replaceLastBotMessageStreaming(botMsg);
});

function markdownToHTML(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") 
    .replace(/\n/g, "<br>");
}

function appendMessage(sender, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}-message`;
  msgDiv.innerHTML = markdownToHTML(text);
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function replaceLastBotMessageStreaming(text) {
  const messages = document.querySelectorAll(".bot-message");
  const lastBot = messages[messages.length - 1];
  if (!lastBot) return;

  const originalHeight = lastBot.offsetHeight;
  lastBot.style.minHeight = `${originalHeight}px`;

  lastBot.innerHTML = "";

  let rendered = "";

  for (let i = 0; i < text.length; i++) {
    rendered += text[i];
    lastBot.innerHTML = markdownToHTML(rendered);

    await new Promise(resolve => setTimeout(resolve, 10));
  }

  lastBot.style.minHeight = "";
}

chatWindow.addEventListener("scroll", () => {
  const nearBottom = chatWindow.scrollHeight - chatWindow.scrollTop <= chatWindow.clientHeight + 50;
  autoScroll = nearBottom;

  if (autoScroll) {
    scrollBtn.style.display = "none";
  } else {
    scrollBtn.style.display = "flex";
  }
});

scrollBtn.addEventListener("click", () => {
  smoothScrollToBottom();
  scrollBtn.style.display = "none";
  autoScroll = true;
});

function smoothScrollToBottom(duration = 800) {
  const start = chatWindow.scrollTop;
  const end = chatWindow.scrollHeight;
  const distance = end - start;
  const startTime = performance.now();

  function animateScroll(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = easeInOutCubic(progress);

    chatWindow.scrollTop = start + distance * ease;

    if (progress < 1) {
      requestAnimationFrame(animateScroll);
    }
  }

  requestAnimationFrame(animateScroll);
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}