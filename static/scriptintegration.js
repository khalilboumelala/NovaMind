document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded. Script is running.');

    const chatForm = document.getElementById('chat-form');
    const startConversationForm = document.querySelector('form[action="/start_conversation"]');
    const chatInput = document.getElementById('prompt');
    const chatWindow = document.getElementById('chat-window');
    const sendBtn = document.getElementById('send-btn');
    const backendUrl = 'http://localhost:5000';

    console.log('chatForm:', chatForm);
    console.log('startConversationForm:', startConversationForm);
    console.log('chatInput:', chatInput);
    console.log('chatWindow:', chatWindow);
    console.log('sendBtn:', sendBtn);

    if (!chatInput) {
        console.error('Chat input not found! Check if <textarea id="prompt"> exists in the HTML.');
        return;
    }
    if (!chatWindow) {
        console.error('Chat window not found! Check if <ul id="chat-window"> exists in the HTML.');
        return;
    }
    if (!sendBtn) {
        console.error('Send button not found! Check if <button id="send-btn"> exists in the HTML.');
        return;
    }

    let isSubmitting = false;

    if (startConversationForm) {
        startConversationForm.addEventListener('submit', (event) => {
            console.log('Start conversation form submitted.');
        });
    }

    if (chatForm) {
        chatForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (isSubmitting) {
                console.log('Submission already in progress. Ignoring duplicate submission.');
                return;
            }
            isSubmitting = true;
            console.log('Chat form submitted! Event listener triggered.');

            console.log('Raw textarea value before trim:', chatInput.value);
            const rawValue = chatInput.value;
            console.log('Forced raw value:', rawValue);
            const userMessage = rawValue.trim();
            console.log('Trimmed user message:', userMessage);
            const mode = document.querySelector('input[name="mode"]:checked')?.value || 'text-only';
            console.log('Selected mode:', mode);

            if (!userMessage) {
                console.log('No message entered. Aborting send.');
                const errorChat = document.createElement('li');
                errorChat.classList.add('chat', 'incoming-chat');
                errorChat.innerHTML = `<span class="material-symbols-outlined">support_agent</span><p>Please enter a message to send.</p>`;
                chatWindow.appendChild(errorChat);
                chatWindow.scrollTop = chatWindow.scrollHeight;
                isSubmitting = false;
                return;
            }

            const userChat = document.createElement('li');
            userChat.classList.add('chat', 'outgoing-chat');
            userChat.innerHTML = `<span class="material-symbols-outlined">person</span><p>${userMessage}</p>`;
            chatWindow.appendChild(userChat);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            console.log('User message displayed in chat window.');

            chatInput.value = '';

            let threadId = chatForm.getAttribute('action').match(/send_message\/(\d+)/)?.[1];
            console.log('Extracted threadId:', threadId);
            if (!threadId) {
                console.error('Thread ID not found in form action. Redirecting to start a new conversation.');
                window.location.href = '/start_conversation';
                isSubmitting = false;
                return;
            }

            const formData = new URLSearchParams();
            formData.append('message', userMessage);
            formData.append('mode', mode);
            console.log(`Sending request to /stream_text with data: prompt=${encodeURIComponent(userMessage)}&mode=${mode}`);

            try {
                const eventSource = new EventSource(`http://127.0.0.1:5000/stream_text?prompt=${encodeURIComponent(userMessage)}`);
                console.log('EventSource created for streaming.');

                let firstChunk = true;
                const botMsg = document.createElement('li');
                botMsg.classList.add('chat', 'incoming-chat');
                const pTag = document.createElement('p');
                pTag.textContent = "🧠 Generating response...";
                botMsg.innerHTML = `<span class="material-symbols-outlined">support_agent</span>`;
                botMsg.appendChild(pTag);
                chatWindow.appendChild(botMsg);
                chatWindow.scrollTop = chatWindow.scrollHeight;
                console.log('Bot message placeholder added.');

                eventSource.onmessage = (event) => {
                    const raw = event.data;
                    console.log('Received stream data:', raw);

                    if (!raw || raw === "[DONE]") {
                        if (raw === "[DONE]") {
                            eventSource.close();
                            console.log('Streaming complete. EventSource closed.');
                            if (mode === 'text-image' || mode === 'image-only') {
                                console.log('Proceeding to image generation.');
                                handleNextSteps(userMessage, pTag, mode, chatWindow); // Pass chatWindow as a parameter
                            }
                            isSubmitting = false;
                        }
                        return;
                    }

                    if (firstChunk) {
                        pTag.innerHTML = "";
                        firstChunk = false;
                        console.log('First chunk received. Clearing placeholder text.');
                    }

                    pTag.dataset.rawText = (pTag.dataset.rawText || "") + raw;
                    const formattedHTML = marked.parse(pTag.dataset.rawText);
                    pTag.innerHTML = formattedHTML;
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                    console.log('Bot response updated in chat window.');
                };

                eventSource.onerror = () => {
                    console.error('EventSource error occurred.');
                    eventSource.close();
                    pTag.textContent = "⚠️ Failed to generate response.";
                    isSubmitting = false;
                };
            } catch (error) {
                console.error('Error sending message:', error);
                const errorChat = document.createElement('li');
                errorChat.classList.add('chat', 'incoming-chat');
                errorChat.innerHTML = `<span class="material-symbols-outlined">support_agent</span><p>Error: ${error.message}</p>`;
                chatWindow.appendChild(errorChat);
                isSubmitting = false;
            }
        });

        sendBtn.addEventListener('click', (event) => {
            console.log('Send button clicked directly.');
            if (isSubmitting) return;
            chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
        });

        chatInput.addEventListener('keydown', (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                console.log('Enter key pressed in textarea.');
                event.preventDefault();
                if (isSubmitting) return;
                chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        });
    } else {
        console.warn('Chat form not found. This is expected if thread_id is none (new conversation).');
    }
});

async function handleNextSteps(promptValue, pTag, mode, chatWindow) { // Add chatWindow as a parameter
    try {
        if (mode === "image-only") {
            const negPrompt = "text, blur, watermark, ugly, distorted";
            console.log('Fetching image for image-only mode with payload:', {
                step: "image",
                prompt_text: promptValue,
                negative_prompt: negPrompt
            });
            const imageRes = await fetch("http://127.0.0.1:5000/generate_step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    step: "image",
                    prompt_text: promptValue,
                    negative_prompt: negPrompt
                })
            });

            console.log('Image fetch response status:', imageRes.status);
            if (!imageRes.ok) {
                throw new Error(`Image fetch failed with status: ${imageRes.status}`);
            }

            const imageData = await imageRes.json();
            console.log('Image data received for image-only mode:', imageData);

            if (!imageData.image) {
                throw new Error('No image data in response');
            }

            renderPreviewCard(null, imageData.image, chatWindow); // Pass chatWindow to renderPreviewCard
            return;
        }

        if (mode === "text-only") {
            return;
        }

        const negMsg = document.createElement("div");
        negMsg.textContent = "🙈 Generating image generation prompt";
        pTag.appendChild(negMsg);
        animateDots(negMsg);

        console.log('Fetching negative prompt with payload:', { prompt: promptValue, step: "negative" });
        const negRes = await fetch("http://127.0.0.1:5000/generate_step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: promptValue, step: "negative" })
        });

        console.log('Negative prompt fetch response status:', negRes.status);
        if (!negRes.ok) {
            throw new Error(`Negative prompt fetch failed with status: ${negRes.status}`);
        }

        const negData = await negRes.json();
        console.log('Negative prompt data:', negData);

        if (!negData.negative) {
            throw new Error('No negative prompt in response');
        }

        const negativePrompt = negData.negative;

        const imgMsg = document.createElement("div");
        imgMsg.textContent = "🎨 Generating image";
        pTag.appendChild(imgMsg);
        animateDots(imgMsg);

        console.log('Fetching image with payload:', {
            step: "image",
            prompt_text: promptValue,
            negative_prompt: negativePrompt
        });
        const imageRes = await fetch("http://127.0.0.1:5000/generate_step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                step: "image",
                prompt_text: promptValue,
                negative_prompt: negativePrompt
            })
        });

        console.log('Image fetch response status:', imageRes.status);
        if (!imageRes.ok) {
            throw new Error(`Image fetch failed with status: ${imageRes.status}`);
        }

        const imageData = await imageRes.json();
        console.log('Image data received:', imageData);

        if (!imageData.image) {
            throw new Error('No image data in response');
        }

        const imageBubble = document.createElement("li");
        imageBubble.classList.add("chat", "incoming-chat");
        imageBubble.dataset.prompt = imageData.image_prompt;
        imageBubble.innerHTML = `
            <span class="material-symbols-outlined">support_agent</span>
            <p>
                <img src="data:image/png;base64,${imageData.image}" alt="Generated Image" style="max-width: 100%; border-radius: 12px;">
                <button class="generate-video-btn">Generate Video</button>
            </p>
        `;
        chatWindow.appendChild(imageBubble);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        console.log('Image bubble added to chat window.');
        stopAnimatingDots();
    } catch (error) {
        console.error('Error in handleNextSteps:', error);
        const errorMsg = document.createElement("div");
        errorMsg.textContent = `⚠️ Failed to generate image: ${error.message}`;
        pTag.appendChild(errorMsg);
        stopAnimatingDots();
    }

    // Add the event listener for the "Generate Video" button outside the try-catch to ensure it’s added even if an error occurs
    const imageBubble = chatWindow.querySelector('.chat:last-child');
    if (imageBubble && imageBubble.querySelector('.generate-video-btn')) {
        imageBubble.querySelector('.generate-video-btn').addEventListener('click', async () => {
            const imgElement = imageBubble.querySelector('img');
            const base64String = imgElement.src.split(',')[1];
            const prompt = imageBubble.dataset.prompt;

            const loadingBubble = document.createElement('li');
            loadingBubble.classList.add('chat', 'incoming-chat');
            loadingBubble.innerHTML = `
                <span class="material-symbols-outlined">support_agent</span>
                <p>🎥 Generating video...</p>
            `;
            chatWindow.appendChild(loadingBubble);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            const byteCharacters = atob(base64String);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/png' });

            const formData = new FormData();
            formData.append('image', blob, 'image.png');
            formData.append('prompt', prompt);

            try {
                const response = await fetch('http://127.0.0.1:5000/generate_video', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) throw new Error('Failed to generate video');
                const videoBlob = await response.blob();
                const videoUrl = URL.createObjectURL(videoBlob);
                loadingBubble.innerHTML = `
                    <span class="material-symbols-outlined">support_agent</span>
                    <p><video src="${videoUrl}" controls style="max-width: 100%; border-radius: 12px;"></video></p>
                `;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            } catch (error) {
                loadingBubble.querySelector('p').textContent = '⚠️ Failed to generate video.';
                console.error('Error:', error);
            }
        });
    }
}

function animateDots(element) {
    let baseText = element.textContent;
    let count = 1;
    clearInterval(window.dotInterval);
    window.dotInterval = setInterval(() => {
        let dots = ".".repeat(count % 4);
        element.textContent = baseText + dots;
        count++;
    }, 500);
}

function cleanMarkdown(text) {
    return text
        .replace(/(#+)([^\s#])/g, "$1 $2")
        .replace(/\n*(#{2,6} .*)/g, "\n\n$1")
        .replace(/•/g, "-")
        .replace(/^[-=]{3,}$/gm, "\n---\n")
        .replace(/(\*\*[^*]+\*\*)([^\s*])/g, "$1\n$2")
        .replace(/([a-zA-Z])(#\w+)/g, "$1 $2")
        .replace(/(\#[\w\d]+)(?=\#)/g, "$1 ")
        .replace(/\*\*/g, "**");
}

function stopAnimatingDots() {
    clearInterval(window.dotInterval);
}

function renderPreviewCard(markdownText = null, imageBase64 = null, chatWindow) { // Add chatWindow as a parameter
    console.log('renderPreviewCard called with:', { markdownText, imageBase64 });
    const card = document.createElement("div");
    card.classList.add("card");

    if (imageBase64) {
        const image = document.createElement("div");
        image.classList.add("card-image");
        image.style.backgroundImage = `url(data:image/png;base64,${imageBase64})`;
        image.style.backgroundSize = "cover";
        card.appendChild(image);
        console.log('Image added to preview card.');
    }

    const category = document.createElement("div");
    category.classList.add("category");
    category.textContent = "Preview";
    card.appendChild(category);

    const heading = document.createElement("div");
    heading.classList.add("heading");

    if (markdownText) {
        const cleaned = cleanMarkdown(markdownText);
        heading.innerHTML = marked.parse(cleaned);
    } else {
        heading.innerHTML = "Visual only preview";
    }

    const author = document.createElement("div");
    author.classList.add("author");
    author.innerHTML = `Generated <span class="name">NovaMind</span> just now`;
    heading.appendChild(author);
    card.appendChild(heading);

    const cardWrapper = document.createElement("li");
    cardWrapper.classList.add("chat", "incoming-chat");
    cardWrapper.appendChild(card);
    chatWindow.appendChild(cardWrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    console.log('Preview card appended to chat window.');
}