const chat = document.getElementById('chat');
const input = document.getElementById('userInput');
const button = document.getElementById('sendBtn');

async function sendMessage(message) {
    const userDiv = document.createElement('div');
    userDiv.className = 'user';
    userDiv.textContent = message;
    chat.appendChild(userDiv);
    chat.scrollTop = chat.scrollHeight;

    try {
        const response = await fetch("http://localhost:3000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        let answer = "Aucune réponse reçue.";
        if (data.choices && data.choices.length > 0) {
            answer = data.choices[0].message.content;
        }

        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'assistant';
        assistantDiv.textContent = answer;
        chat.appendChild(assistantDiv);
        chat.scrollTop = chat.scrollHeight;

    } catch (err) {
        console.error("Erreur fetch frontend:", err);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'assistant';
        errorDiv.textContent = "Erreur serveur. Vérifie la console du backend.";
        chat.appendChild(errorDiv);
    }
}

button.addEventListener('click', () => {
    if (input.value.trim() !== "") {
        sendMessage(input.value.trim());
        input.value = "";
    }
});

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && input.value.trim() !== "") {
        sendMessage(input.value.trim());
        input.value = "";
    }
});