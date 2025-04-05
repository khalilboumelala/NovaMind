document.addEventListener("DOMContentLoaded", () => {
    const promptField = document.getElementById("prompt");
    const chatWindow = document.querySelector(".chat-window");
    const sendBtn = document.getElementById("send-btn");

    const sendChat = async() => {
        const promptValue = promptField.value.trim();
        if (!promptValue) return alert("Please enter a prompt!");

        let userMsg = document.createElement("li");
        userMsg.classList.add("chat", "outgoing-chat");
        userMsg.innerHTML = `<p>${promptValue}</p>`;
        chatWindow.appendChild(userMsg);

        let botMsg = document.createElement("li");
        botMsg.classList.add("chat", "incoming-chat");
        let pTag = document.createElement("p");
        pTag.textContent = "🧠 Generating post text...";
        botMsg.innerHTML = `<span class="material-symbols-outlined">support_agent</span>`;
        botMsg.appendChild(pTag);
        chatWindow.appendChild(botMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        promptField.value = "";

        try {
            // Step 1: Generate text
            const textRes = await fetch("http://127.0.0.1:5000/generate_step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: promptValue, step: "text" })
            });
            const textData = await textRes.json();
            pTag.textContent = "🙈 Generating negative prompt...";
            const finalText = textData.text;

            // Step 2: Generate negative prompt
            const negRes = await fetch("http://127.0.0.1:5000/generate_step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: promptValue, step: "negative" })
            });
            const negData = await negRes.json();
            pTag.textContent = "🎨 Generating image...";
            const negativePrompt = negData.negative;

            // Step 3: Generate image
            const imageRes = await fetch("http://127.0.0.1:5000/generate_step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    step: "image",
                    prompt_text: promptValue,
                    negative_prompt: negativePrompt
                })
            });
            const imageData = await imageRes.json();

            pTag.innerHTML = `<strong>${finalText}</strong><br><img src="data:image/png;base64,${imageData.image}" alt="Generated Image">`;
        } catch (error) {
            console.error(error);
            pTag.textContent = "⚠️ Error generating post.";
        }

        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    promptField.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendChat();
        }
    });

    sendBtn.addEventListener("click", sendChat);
});