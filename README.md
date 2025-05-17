# Basic Chatbot

This repository contains a **Basic Chatbot** built with HTML, CSS, and JavaScript, utilizing a Large Language Model (LLM) through API calls. The chatbot can interact with users, provide automated responses, and leverage the power of an LLM for more advanced natural language understanding.

## Features

- **Interactive UI**: A simple and intuitive user interface using HTML/CSS.
- **LLM Integration**: Powered by a Large Language Model through API calls.
- **JavaScript-based**: Handles all logic on the client-side using JavaScript.
- **Scalable Design**: Easy to extend with more sophisticated LLM models or APIs.

## Getting Started

### Prerequisites

Before running the project, you will need:

- A web browser (latest version of Chrome, Firefox, etc.)
- An API key for accessing the LLM (e.g., OpenAI, GPT-based models, or others).

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/KidronL/basic_chatbot.git
   ```

2. Navigate into the project directory:

   ```bash
   cd basic_chatbot
   ```

3. Open the `index.html` file in your browser:

   ```bash
   open index.html
   ```

### Configuration

To integrate with your preferred LLM, you will need to modify the `script.js` file and include your API key and endpoint URL. (Gemini's API requests are currently free and so I suggest using that, as that is what this was built with.)

```javascript
const API_KEY = 'your-api-key-here';
const API_URL = 'https://api.your-llm-provider.com/v1/chat';
```

### Usage

1. Once the project is open in your browser, type a message in the input box.
2. The chatbot will respond by making an API call to the configured LLM and display the response in the chat window.

## API Integration

This project uses fetch API in JavaScript with the Gemini model to make requests to an external LLM provider. Here's how you would format the API if you would like to utilize OpenAI's GPT model:

```javascript
fetch(API_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
  },
  body: JSON.stringify({
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": userMessage}]
  })
})
.then(response => response.json())
.then(data => {
  // Handle chatbot response here
});
```

## Contact

For any questions or suggestions, feel free to reach out via [GitHub Issues](https://github.com/KidronL/basic_chatbot/issues).
```

This version includes details relevant to the API-based LLM integration and front-end setup. Let me know if you need any adjustments!