
function sendQuestion() {
    const question = document.getElementById("taxPrompt").value;
    const responseBox = document.getElementById("response");

    // Create an AJAX request
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:8000/api/tax-question", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                const answer = data.answer[0].text || "No answer provided.";


                appendMessage("You", question);
                appendMessage("Bot", answer);

                // Save the conversation to localStorage
                saveConversation("You", question);
                saveConversation("Bot", answer);
            } else {
                responseBox.innerHTML = "Error connecting to server.";
            }
        }
    };

    // Send the request with the question as payload
    xhr.send(JSON.stringify({ question: question }));

    // Clear the input field
    clearPrompt();
}

// Function to clear the prompt input field
function clearPrompt() {
    document.getElementById("taxPrompt").value = '';
}

// Function to append a message to the response box
function appendMessage(sender, message) {
    const responseBox = document.getElementById("response");
    responseBox.innerHTML += `<strong>${sender}:</strong> ${message}<br>`;
}

// Function to save conversation messages to localStorage
function saveConversation(sender, message) {
    let conversation = JSON.parse(localStorage.getItem("conversation")) || [];
    conversation.push({ sender, message });
    localStorage.setItem("conversation", JSON.stringify(conversation));
}

// Function to load conversation history from localStorage on page load
function loadConversation() {
    localStorage.removeItem("conversation");
    const responseBox = document.getElementById("response");
    const conversation = JSON.parse(localStorage.getItem("conversation")) || [];
    conversation.forEach(msg => {
        responseBox.innerHTML += `<strong>${msg.sender}:</strong> ${msg.message}<br>`;
    });
}

// Load the conversation when the page is loaded
window.onload = loadConversation;
