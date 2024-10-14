// URL parametrelerini alıyoruz
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('userId');

// Kanbanları yükleyip listeye ekliyoruz
fetch(`http://127.0.0.1:8000/users/${userId}/project`)
    .then(response => response.json())
    .then(data => {
        const kanbanList = document.getElementById('kanban-list');
        kanbanList.innerHTML = ''; // Önceki listeyi temizliyoruz

        // Her bir Kanban için liste öğesi oluşturuyoruz
        data.forEach(kanban => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = `kanban.html?userId=${userId}&kanbanId=${kanban.kanbanId}`;
            link.textContent = `${kanban.kanbanName} -- Kanban ID: ${kanban.kanbanId} --`;
            listItem.appendChild(link);
            kanbanList.appendChild(listItem);
        });
    })
    .catch(error => console.error('Kanbanlar alınırken bir hata oluştu:', error));

// Yeni Kanban oluşturma işlemi
document.getElementById('create-kanban-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Formun varsayılan gönderme davranışını engelliyoruz

    const kanbanName = document.getElementById('kanbanName').value;

    // Yeni Kanban oluşturmak için API'ye istek gönderiyoruz
    fetch(`http://127.0.0.1:8000/users/${userId}/project`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ kanbanName }),
    })
        .then(response => response.json())
        .then(data => {
            // Yeni Kanban'ı listeye ekliyoruz
            const kanbanList = document.getElementById('kanban-list');
            const listItem = document.createElement('li');
            const link = document.createElement('a');

            link.href = `kanban.html?userId=${userId}&kanbanId=${data.kanbanId}`;
            link.textContent = data.kanbanName;

            listItem.appendChild(link);
            kanbanList.appendChild(listItem);
        })
        .catch(error => console.error('Yeni Kanban oluşturulurken bir hata oluştu:', error));
});

// Kanban silme işlemi
document.getElementById('delete-kanban-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Formun varsayılan gönderme davranışını engelliyoruz

    const kanbanId = document.getElementById('kanbanId').value;

    // Kanban ID'sinin boş olmadığından emin oluyoruz
    if (!kanbanId) {
        console.error('Kanban ID’si gereklidir');
        return;
    }

    // Kanban'ı silmek için API'ye istek gönderiyoruz
    fetch(`http://127.0.0.1:8000/projects/${kanbanId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => {
            if (response.ok) {
                console.log('Kanban başarıyla silindi');
                // Kanban'ı listeden kaldırıyoruz
                removeKanbanFromList(kanbanId);
            } else {
                console.error('Kanban silinirken bir hata oluştu:', response.statusText);
            }
        })
        .catch(error => console.error('Kanban silinirken bir hata oluştu:', error));
});

// Kanban'ı listeden kaldırma fonksiyonu
function removeKanbanFromList(kanbanId) {
    const kanbanList = document.getElementById('kanban-list');
    const listItems = kanbanList.getElementsByTagName('li');

    for (let i = 0; i < listItems.length; i++) {
        const listItem = listItems[i];
        const link = listItem.getElementsByTagName('a')[0];
        if (link && link.href.includes(`kanbanId=${kanbanId}`)) {
            kanbanList.removeChild(listItem);
            break; // İlk eşleşen öğeyi bulduktan sonra döngüyü kırıyoruz
        }
    }
}

// Kullanıcı bilgilerini yükleme fonksiyonu
async function loadUser() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`);
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');
        }
        const user = await response.json();
        document.getElementById('username').textContent = user.userName || 'Kullanıcı Adı';

    } catch (error) {
        console.error('Kullanıcı bilgileri yüklenirken bir hata oluştu:', error);
    }
}

// Sayfa yüklendiğinde kullanıcı bilgilerini yüklüyoruz
loadUser();
