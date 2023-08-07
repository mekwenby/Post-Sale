document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const imageInput = document.getElementById('image-input');

    sendButton.addEventListener('click', function () {
        const message = messageInput.value.trim();
        if (message !== '') {
            appendMessage('You', message, false);
            // Simulate receiver's response after 1 second
            setTimeout(() => {
                appendMessage('Receiver', 'Hello from the other side!', true);
            }, 1000);
            messageInput.value = '';
        }
    });

    imageInput.addEventListener('change', function () {
        const file = imageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                const image = document.createElement('img');
                image.src = event.target.result;
                appendMessage('You', image, false);
            };
            reader.readAsDataURL(file);
        }
    });

    function appendMessage(sender, content, isReceiver) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('alert', 'mb-2');
        if (isReceiver) {
            messageElement.classList.add('receiver-message');
        } else {
            messageElement.classList.add('alert-primary');
        }

        if (typeof content === 'string') {
            messageElement.innerText = sender + ': ' + content;
        } else if (content instanceof Element) {
            if (content.tagName.toLowerCase() === 'img') {
                content.classList.add('image-message');
            }
            const senderSpan = document.createElement('span');
            senderSpan.innerText = sender + ': ';
            messageElement.appendChild(senderSpan);
            messageElement.appendChild(content);
        }

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
    }
});