// Kullanıcı ekleme fonksiyonu
async function addUser() {
    try {
        // Kullanıcı verilerini API'den al
        const response = await fetch('http://127.0.0.1:8000/users/');
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');  // Ağ hatası durumunda hata fırlat
        }
        const data = await response.json();
        console.log('Kullanıcılar:', data);  // Kullanıcı verilerini kontrol et

        const userList = document.getElementById('username');
        if (userList) {  // user-list elemanının mevcut olduğundan emin ol
            userList.innerHTML = '';  // Listeyi temizle
            const div = document.createElement('div');
            div.textContent = data.userName;  // Kullanıcı adını ekrana yazdır
            userList.appendChild(div);  // Kullanıcı adını listeye ekle
        } else {
            console.error('Kullanıcı listesi elemanı bulunamadı');  // Eleman bulunamazsa hata mesajı yazdır
        }
    } catch (error) {
        console.error('Kullanıcıları yüklerken hata oluştu:', error);  // Verileri yüklerken hata oluşursa hata mesajını konsola yazdır
    }
}
