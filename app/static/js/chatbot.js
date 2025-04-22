// app/static/js/chatbot.js
document.addEventListener('DOMContentLoaded', function() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotHeader = document.getElementById('chatbot-header');
    const chatbotBody = document.getElementById('chatbot-body');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotText = document.getElementById('chatbot-text');
    const chatbotSend = document.getElementById('chatbot-send');

    // Toggle chatbot visibility
    chatbotHeader.addEventListener('click', function() {
        chatbotBody.style.display = chatbotBody.style.display === 'none' ? 'block' : 'none';
    });

    // Send message
    chatbotSend.addEventListener('click', function() {
        const message = chatbotText.value;
        if (message) {
            // Display user message
            displayMessage('user', message);

            // Get recommendation
            const recommendation = getRecommendation(message);

            // Display chatbot message
            displayMessage('chatbot', recommendation);

            // Clear input
            chatbotText.value = '';
        }
    });

    // Get book recommendation
    function getRecommendation(message) {
        message = message.toLowerCase();

        if (message.includes('fantasy')) {
            return 'I recommend "The Hobbit" by J.R.R. Tolkien.';
        } else if (message.includes('science fiction')) {
            return 'I recommend "Dune" by Frank Herbert.';
        } else if (message.includes('mystery')) {
            return 'I recommend "The Girl with the Dragon Tattoo" by Stieg Larsson.';
        } else {
            return 'I recommend "Pride and Prejudice" by Jane Austen.';
        }
    }

    // Display message
    function displayMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chatbot-message');
        messageElement.classList.add(sender);
        messageElement.textContent = message;
        chatbotMessages.appendChild(messageElement);

        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
});