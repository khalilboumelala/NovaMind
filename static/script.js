document.addEventListener("DOMContentLoaded", () => {
    const promptField = document.getElementById("prompt");
    const chatWindow = document.querySelector(".chat-window");
    const sendBtn = document.getElementById("send-btn");

    const sendChat = async() => {
        const promptValue = promptField.value.trim();
        if (!promptValue) return alert("Please enter a prompt!");
        const selectedMode = document.querySelector('input[name="mode"]:checked').value;

        let userMsg = document.createElement("li");
        userMsg.classList.add("chat", "outgoing-chat");
        userMsg.innerHTML = `<p>${promptValue}</p>`;
        chatWindow.appendChild(userMsg);

        let botMsg = document.createElement("li");
        botMsg.classList.add("chat", "incoming-chat");
        const pTag = document.createElement("p");
        pTag.textContent = "🧠 Generating post text...";
        botMsg.innerHTML = `<span class="material-symbols-outlined">support_agent</span>`;
        botMsg.appendChild(pTag);
        chatWindow.appendChild(botMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        promptField.value = "";

        // STEP 1: STREAMED TEXT GENERATION
        const eventSource = new EventSource(`http://127.0.0.1:5000/stream_text?prompt=${encodeURIComponent(promptValue)}`);


        let firstChunk = true;



        eventSource.onmessage = (event) => {
            const raw = event.data;

            if (!raw || raw === "[DONE]") {
                if (raw === "[DONE]") {
                    eventSource.close();
                    sendBtn.disabled = false;
                    handleNextSteps(promptValue, pTag, selectedMode);
                }
                return;
            }

            if (firstChunk) {
                pTag.innerHTML = ""; // Clear old loading text
                firstChunk = false;
            }

            // Use marked to parse full markdown content (accumulate then parse)
            pTag.dataset.rawText = (pTag.dataset.rawText || "") + raw;

            // Use `marked` to convert rawText into HTML
            const cleaned = cleanMarkdown(pTag.dataset.rawText);
            const formattedHTML = marked.parse(cleaned);
            pTag.innerHTML = formattedHTML;

            chatWindow.scrollTop = chatWindow.scrollHeight;
        };

        eventSource.onerror = () => {
            eventSource.close();
            pTag.textContent = "⚠️ Failed to generate text.";
        };
    };

    async function handleNextSteps(promptValue, pTag, mode) {
        // STEP 2: GENERATE NEGATIVE PROMPT
        // Preserve previous HTML

        if (mode === "image-only") {
            // Just generate image
            const negPrompt = getNegativePrompt("default");
            const imageRes = await fetch("http://127.0.0.1:5001/generate_step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    step: "image",
                    prompt_text: promptValue,
                    negative_prompt: negPrompt
                })
            });
            const imageData = await imageRes.json();
            renderPreviewCard(null, imageData.image);
            return;
        }

        if (mode === "text-only") {
            return; // Only streamed text was shown, so just stop here
        }

        const negMsg = document.createElement("div");
        negMsg.textContent = "🙈 Generating image generation prompt";
        pTag.appendChild(negMsg);
        animateDots(negMsg); // animate dots only on the new line

        const negRes = await fetch("http://127.0.0.1:5001/generate_step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: promptValue, step: "negative" })
        });
        const negData = await negRes.json();
        const negativePrompt = negData.negative;

        // STEP 3: GENERATE IMAGE
        const imgMsg = document.createElement("div");
        imgMsg.textContent = "🎨 Generating image";
        pTag.appendChild(imgMsg);
        animateDots(imgMsg);

        const imageRes = await fetch("http://127.0.0.1:5001/generate_step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                step: "image",
                prompt_text: promptValue,
                negative_prompt: negativePrompt
            })
        });
        const imageData = await imageRes.json();

        // Store the image and its specific prompt
        const imageBubble = document.createElement("li");
        imageBubble.classList.add("chat", "incoming-chat");
        imageBubble.dataset.prompt = imageData.image_prompt; // Store the specific image prompt
        imageBubble.innerHTML = `
            <span class="material-symbols-outlined">support_agent</span>
            <p>
                <img src="data:image/png;base64,${imageData.image}" alt="Generated Image" style="max-width: 100%; border-radius: 12px;">
                <button class="generate-video-btn">Generate Video</button>
            </p>
        `;
        chatWindow.appendChild(imageBubble);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        stopAnimatingDots();

        // Add event listener for the "Generate Video" button
        imageBubble.querySelector('.generate-video-btn').addEventListener('click', async() => {
            const imgElement = imageBubble.querySelector('img');
            const base64String = imgElement.src.split(',')[1];
            const prompt = imageBubble.dataset.prompt; // Retrieve the specific image prompt

            // Show loading message
            const loadingBubble = document.createElement('li');
            loadingBubble.classList.add('chat', 'incoming-chat');
            loadingBubble.innerHTML = `
                <span class="material-symbols-outlined">support_agent</span>
                <p>🎥 Generating video...</p>
            `;
            chatWindow.appendChild(loadingBubble);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            // Convert base64 to Blob
            const byteCharacters = atob(base64String);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/png' });

            // Prepare FormData with image and specific prompt
            const formData = new FormData();
            formData.append('image', blob, 'image.png');
            formData.append('prompt', prompt); // Send the specific image prompt

            try {
                const response = await fetch('http://127.0.0.1:5001/generate_video', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to generate video');
                }
                const videoBlob = await response.blob();
                const videoUrl = URL.createObjectURL(videoBlob);

                // Display video
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

    // Dot Animation
    let dotInterval;

    function animateDots(element) {
        let baseText = element.textContent;
        let count = 1;
        clearInterval(dotInterval);
        dotInterval = setInterval(() => {
            let dots = ".".repeat(count % 4);
            element.textContent = baseText + dots;
            count++;
        }, 500);
    }

    function formatText(rawText) {
        return marked.parse(
            rawText
            .replace(/(\*\*.*?\*\*)([^\n*])/g, "$1\n$2") // Ensure newline after bold if missing
            .replace(/([a-zA-Z0-9])(#\w+)/g, "$1 $2") // Ensure space before hashtags
        );
    }

    function cleanMarkdown(text) {
        return text
            // Fix missing space after heading markers
            .replace(/(#+)([^\s#])/g, "$1 $2")

        // Force a line break before any heading to separate it
        .replace(/\n*(#{2,6} .*)/g, "\n\n$1")

        // Convert • bullets into proper markdown list items
        .replace(/•/g, "-")

        // Convert manual divider lines to real horizontal rules
        .replace(/^[-=]{3,}$/gm, "\n---\n")

        // Add line breaks after bold blocks that are followed by text
        .replace(/(\*\*[^*]+\*\*)([^\s*])/g, "$1\n$2")

        // Ensure space before hashtags
        .replace(/([a-zA-Z])(#\w+)/g, "$1 $2")

        // Fix jammed hashtags at the end
        .replace(/(\#[\w\d]+)(?=\#)/g, "$1 ")

        // Ensure line breaks between lines that start with *
        .replace(/\*\*/g, "**");
    }


    function stopAnimatingDots() {
        clearInterval(dotInterval);
    }

    function renderPreviewCard(markdownText = null, imageBase64 = null) {
        const card = document.createElement("div");
        card.classList.add("card");

        if (imageBase64) {
            const image = document.createElement("div");
            image.classList.add("card-image");
            image.style.backgroundImage = `url(data:image/png;base64,${imageBase64})`;
            image.style.backgroundSize = "cover";
            card.appendChild(image);
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
    }


    promptField.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendChat();
        }
    });

    sendBtn.addEventListener("click", sendChat);
});