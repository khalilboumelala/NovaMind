document.addEventListener("DOMContentLoaded", () => {
    const promptField = document.getElementById("prompt");
    const negativePromptField = document.getElementById("negativePrompt");
    const chatWindow = document.querySelector(".chat-window");

    const sendChat = async () => {
        const promptValue = promptField.value.trim();
        const negativeValue = negativePromptField.value.trim();

        if (!promptValue) return alert("Please enter a prompt!");

        // Show user message
        let userMsg = document.createElement("li");
        userMsg.classList.add("chat", "outgoing-chat");
        userMsg.innerHTML = `<p>${promptValue}</p>`;
        chatWindow.appendChild(userMsg);

        // Show bot generating feedback
        let botMsg = document.createElement("li");
        botMsg.classList.add("chat", "incoming-chat");
        botMsg.innerHTML = `<span class="material-symbols-outlined">support_agent</span>
                            <p>Generating image...</p>`;
        chatWindow.appendChild(botMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const response = await fetch("http://127.0.0.1:7860/sdapi/v1/txt2img", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: promptValue,
                    negative_prompt: negativeValue,
                    steps: 20,
                    cfg_scale: 7,
                    width: 512,
                    height: 512,
                    seed: -1
                })
            });

            if (!response.ok) throw new Error("Failed to fetch image");
            const data = await response.json();
            const imageBase64 = data.images[0];

            // Replace 'Generating...' with the image
            botMsg.innerHTML = `<span class="material-symbols-outlined">support_agent</span>
                                <p><img src="data:image/png;base64,${imageBase64}" alt="Generated Image"></p>`;
        } catch (error) {
            console.error("Error:", error);
            botMsg.querySelector("p").textContent = "Error generating image, please try again!";
        }

        chatWindow.scrollTop = chatWindow.scrollHeight;
        promptField.value = "";
        negativePromptField.value = "";
    };

    // Handle Enter key press
    promptField.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // Prevents new line
            sendChat();
        }
    });

    // Attach click event to the send button
    document.getElementById("send-btn").addEventListener("click", sendChat);
});
