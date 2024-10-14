const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('userId');

// Kullanıcı verilerini asenkron olarak yükleyen fonksiyon
async function loadUser() {
    try {
        // Kullanıcı verilerini API'den al
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');  // Ağ hatası durumunda hata fırlat
        }

        const user = await response.json();
        console.log('User Data:', user);  // Kullanıcı verilerini kontrol et

        // Kullanıcı verilerini form alanlarına yerleştir
        document.getElementById('user').placeholder = user.userName || 'New Username';  // Kullanıcı adı yer tutucusu
        document.getElementById('email').placeholder = user.userEmail || 'New Email';  // E-posta yer tutucusu

        // Kullanıcı adını ilgili div içine yerleştir
        document.getElementById('username').textContent = user.userName || 'Username';  // Kullanıcı adı

    } catch (error) {
        console.error('Failed to load user data:', error);  // Verileri yüklerken bir hata oluşursa hata mesajını konsola yazdır
    }
}

loadUser();
