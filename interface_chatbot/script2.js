const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const chatWindow = document.querySelector(".chat-window");
const chatBotOpener = document.querySelector(".chatbot-opener");
const chatBotCloseBtn = document.querySelector(".close-btn");

let userMessage;
//Please utilize your own Gemeni
const API_KEY = "";
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    // Creating a chat line element with the passed message and class name.
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = className === "outgoing-chat" ? `<p></p>` : `<span class="material-symbols-outlined">support_agent</span><p></p>`
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const generateResponse = (incomingChatLi) => {
    const API_URL = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`
    const messageElement = incomingChatLi.querySelector("p");

    //Building the API call through a POST method
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            contents: [{role: "user", parts: [{text: userMessage}]}]
        }),
    }

    //Response from POST request
    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        messageElement.textContent = data.candidates[0].content.parts[0].text; // Update message text with API response
    }).catch((error) => {
        messageElement.classList.add("error");
        messageElement.textContent = "Something went wrong.";
    }).finally(() => chatWindow.scrollTo(0, chatWindow.scrollHeight));
}

const handleChat = () => {
    userMessage = chatInput.value.trim();
    if(!userMessage) return;
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    //Appending the user's message to the chat window
    chatWindow.appendChild(createChatLi(userMessage, "outgoing-chat"));
    chatWindow.scrollTo(0, chatWindow.scrollHeight);

    setTimeout(() => {
        //Showing a default message while waiting for a response
        const incomingChatLi = createChatLi("Thinking...", "incoming-chat");
        chatWindow.appendChild(incomingChatLi);
        chatWindow.scrollTo(0, chatWindow.scrollHeight);
        generateResponse(incomingChatLi);   
    }, 600);

};

chatInput.addEventListener("input", () => {
    //Auto adujusting height based on input
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
})

chatInput.addEventListener("keyup", (e) => {
    //Allowing the use of the enter key to send messages
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
})

//chatBotCloseBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
//chatBotOpener.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
sendChatBtn.addEventListener("click", handleChat);

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("send-btn").addEventListener("click", async () => {
        const promptField = document.getElementById("prompt");
        const negativePromptField = document.getElementById("negativePrompt");
        const promptValue = promptField.value.trim();
        const negativeValue = negativePromptField.value.trim();
        const chatWindow = document.querySelector(".chat-window");

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
    });
});