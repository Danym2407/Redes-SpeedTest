// Función para mostrar/ocultar el chatbot
function toggleChat() {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.classList.toggle("hidden");
}

// Función que se ejecuta cuando el usuario envía un mensaje
// Función para enviar el mensaje y recibir la respuesta del chatbot
function sendMessage() {
    const message = document.getElementById("message-box").value;

    // Si el mensaje está vacío, no hacer nada
    if (message.trim() === "") return;

    // Agregar el mensaje del usuario al chat (lado derecho)
    addMessageToChat(message, "sent");

    // Mostrar la animación "escribiendo..."
    addTypingIndicator();

    // Limpiar el cuadro de entrada
    document.getElementById("message-box").value = "";

    // Hacer la solicitud POST a Flask
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Remover la animación "escribiendo"
        removeTypingIndicator();
        
        // Agregar la respuesta del chatbot al chat (lado izquierdo)
        const reply = data.response;
        addMessageToChat(reply, "received");
    })
    .catch(error => {
        console.error("Error:", error);
        removeTypingIndicator();
    });
}

// Agregar el mensaje recibido al chat
function addMessageToChat(message, type) {
    const chatBody = document.getElementById("chat-body");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", type);
    messageElement.textContent = message;
    chatBody.appendChild(messageElement);
    chatBody.scrollTop = chatBody.scrollHeight;  // Mantener el scroll al final
}

// Configuración para enviar el mensaje cuando presionas "Enter"
document.getElementById("message-box").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage(); // Enviar el mensaje cuando se presiona "Enter"
    }
});



// Función para agregar la animación de "escribiendo"
function addTypingIndicator() {
    const chatBody = document.getElementById("chat-body");
    const typingElement = document.createElement("div");
    typingElement.classList.add("typing-indicator");
    typingElement.textContent = "Escribiendo...";
    chatBody.appendChild(typingElement);
}

// Función para eliminar la animación de "escribiendo"
function removeTypingIndicator() {
    const typingElements = document.getElementsByClassName("typing-indicator");
    if (typingElements.length > 0) {
        typingElements[0].remove();
    }
}