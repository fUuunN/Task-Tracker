// Kullanıcı verilerini yükleyen asenkron fonksiyon
async function loadUsers() {
    try {
        // API'den kullanıcı verilerini al
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`);
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');  // Ağ yanıtı uygun değilse hata fırlat
        }
        const data = await response.json();
        console.log('Kullanıcılar:', data);  // Kullanıcı verilerini kontrol et

        const userList = document.getElementById('username');
        if (userList) {  // Kullanıcı liste elemanının mevcut olduğundan emin ol
            userList.innerHTML = '';  // Listeyi temizle
            const div = document.createElement('div');
            div.textContent = data.userName;  // Kullanıcı adını ekrana yazdır
            userList.appendChild(div);  // Kullanıcı adını listeye ekle
        } else {
            console.error('Kullanıcı listesi elemanı bulunamadı');  // Kullanıcı listesi elemanı bulunamazsa hata mesajı yazdır
        }
    } catch (error) {
        console.error('Kullanıcıları yüklerken hata oluştu:', error);  // Kullanıcıları yüklerken hata oluşursa hata mesajını konsola yazdır
    }
}

// Sayfa yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function () {
    console.log('Sayfa yüklendi');
    loadTasks();  // Görevleri yükle
    loadUsers();  // Kullanıcıları yükle
    loadKanbans();  // Kanbanları yükle
});

// Sayfada herhangi bir yere tıklama olayını işleyen fonksiyon
document.addEventListener('click', function (event) {
    console.log('Tıklama olayı tetiklendi');
    // Olay nesnesinin mevcut olduğundan emin ol
    if (!event || !event.target) {
        console.error('Olay veya olay hedefi tanımlı değil');
        return;
    }

    // Tıklanan öğeyle işlem yap
    const targetElement = event.target;
    console.log('Tıklanan öğe:', targetElement);

    // Tıklanan öğeyle yapmanız gereken işlemleri buraya ekleyin
});

// Navbar (Gezinme menüsü) açma/kapama işlevi
document.addEventListener('DOMContentLoaded', () => {
    const usernameContainer = document.getElementById('username-container');
    const userMenu = document.getElementById('user-menu');

    // Kullanıcı menüsünü açma/kapatma
    usernameContainer.addEventListener('click', () => {
        userMenu.style.display = userMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Dışarı tıklama ile menüyü kapama
    window.addEventListener('click', (event) => {
        if (!usernameContainer.contains(event.target)) {
            userMenu.style.display = 'none';
        }
    });

    // Profil ve ayarlar bağlantıları
    const profileLink = document.getElementById('profile-link');
    const settingsLink = document.getElementById('settings-link');

    profileLink.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = `/app/templates/profil.html?userId=${userId}`;
    });

    settingsLink.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = `/app/templates/setting.html?userId=${userId}`;
    });
});