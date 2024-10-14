document.addEventListener('DOMContentLoaded', function () {
    // Elemanları seçiyoruz
    const chatToggle = document.getElementById('chat-toggle');
    const chatContainer = document.getElementById('chat-container');
    const chatClose = document.getElementById('chat-close');
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');

    // URL parametrelerini alıyoruz
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('userId'); // Gerçek kullanıcı ID'sini buradan dinamik olarak alabiliriz

    // Chat penceresini açma
    chatToggle.addEventListener('click', function () {
        chatContainer.classList.add('show'); // 'show' sınıfını ekleyerek chat penceresini görünür yapıyoruz
    });

    // Chat penceresini kapama
    chatClose.addEventListener('click', function () {
        chatContainer.classList.remove('show'); // 'show' sınıfını çıkararak chat penceresini gizliyoruz
    });

    // Mesaj formunu gönderme
    chatForm.addEventListener('submit', async function (event) {
        event.preventDefault(); // Formun varsayılan gönderme davranışını engelliyoruz

        const input = userInput.value.trim(); // Kullanıcı girişini alıyoruz ve boşlukları temizliyoruz
        if (input === '') {
            return; // Boş girişleri işleme
        }

        // Kullanıcı mesajını ekliyoruz
        appendMessage('user', `You: ${input}`);

        try {
            // Bot yanıtını almak için API'ye istek gönderiyoruz
            const response = await fetch(`http://localhost:8000/chatbot?user_input=${encodeURIComponent(input)}&userId=${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Ağ yanıtı uygun değil'); // Yanıt uygun değilse hata fırlatıyoruz
            }

            const data = await response.json(); // Yanıtı JSON formatında alıyoruz

            // Bot yanıtını ekliyoruz
            appendMessage('bot', `Bot: ${data.message}`);

        } catch (error) {
            console.error('Fetch işlemi sırasında bir sorun oluştu:', error); // Hata durumunda konsola yazdırıyoruz

            // Hata mesajını ekliyoruz
            appendMessage('bot', 'Bot: Bir hata oluştu. Lütfen tekrar deneyin.');
        }

        // Giriş alanını temizliyoruz
        userInput.value = '';

        // Chatbox'ı en son mesaja kaydırıyoruz
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Mesajları chatbox'a ekleyen fonksiyon
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${sender}`; // Mesajın göndericisine göre sınıf ekliyoruz
        messageElement.innerHTML = message; // Mesaj içeriğini ayarlıyoruz
        chatBox.appendChild(messageElement); // Mesajı chatbox'a ekliyoruz
    }
});
