// URL parametrelerini alıyoruz
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('userId');
const kanbanId = urlParams.get('kanbanId');

// Görevleri yükleyen fonksiyon
async function loadTasks() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}/project/kanban/${kanbanId}`);
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');
        }

        const kanbanData = await response.json();
        const tasks = kanbanData.tasks;

        // Görev listesi konteynerlerini tanımlıyoruz
        const containers = {
            1: document.getElementById('task-list-todo'),
            2: document.getElementById('task-list-devam-ediyor'),
            3: document.getElementById('task-list-bitmis')
        };

        // Tüm konteynerlerin içeriğini temizliyoruz
        Object.values(containers).forEach(container => {
            if (container) {
                container.innerHTML = '';
            } else {
                console.error('Görev listesi konteyneri bulunamadı');
            }
        });

        // Görevleri uygun konteynerlere ekliyoruz
        tasks.forEach(task => {
            const container = containers[task.statusId];
            if (container) {
                const div = createTaskElement(task);
                container.appendChild(div);
            } else {
                console.error('Durum ID\'si için görev listesi konteyneri bulunamadı:', task.statusId);
            }
        });
    } catch (error) {
        console.error('Görevler yüklenirken bir hata oluştu:', error);
    }
}

// Görev öğesi oluşturan fonksiyon
function createTaskElement(task) {
    const div = document.createElement('div');
    div.className = 'task-item';

    const infoDiv = document.createElement('div');
    infoDiv.className = 'task-info';
    infoDiv.innerHTML = `<div><strong>${task.taskName || 'N/A'}</strong></div>`;

    const button = document.createElement('button');
    button.textContent = 'Show Details';
    button.className = 'toggle-button';

    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'task-details';
    detailsDiv.style.display = 'none';

    detailsDiv.innerHTML = `
        <div><strong>Görev Açıklaması:</strong> ${task.taskDescription || 'N/A'}</div>
        <div><strong>Atanan Kullanıcı:</strong> ${task.assignedToUser || 'N/A'}</div>
        <div><strong>Görev Güncellendiği Zaman:</strong> ${new Date(task.taskUpdatedAt).toLocaleString() || 'N/A'}</div>
    `;

    // Detayları göster/gizle butonuna işlev ekliyoruz
    button.addEventListener('click', () => {
        if (detailsDiv.style.display === 'none') {
            detailsDiv.style.display = 'block';
            button.textContent = 'Hide Details';
        } else {
            detailsDiv.style.display = 'none';
            button.textContent = 'Show Details';
        }
    });

    // Görevi silmek için buton oluşturuyoruz
    const deleteButton = createButton('Delete', 'delete-button', async () => {
        try {
            const deleteResponse = await fetch(`http://127.0.0.1:8000/tasks/${task.taskId}`, {
                method: 'DELETE'
            });

            if (deleteResponse.ok) {
                alert('Görev başarıyla silindi!');
                div.remove();
            } else {
                const error = await deleteResponse.json();
                alert(`Hata: ${error.detail}`);
            }
        } catch (error) {
            alert(`Hata: ${error.message}`);
        }
    });

    // Görevi güncellemek için buton oluşturuyoruz
    const updateButton = createButton('Update', 'update-button', () => {
        document.getElementById('update-task-id').value = task.taskId;
        document.getElementById('update-task-title').value = task.taskName;
        document.getElementById('update-task-status').value = task.statusId;
        document.getElementById('update-task-description').value = task.taskDescription;
        document.getElementById('update-task-assigned-user').value = task.assignedToUser;

        document.getElementById('update-task-modal').style.display = 'block';
    });

    div.appendChild(infoDiv);
    div.appendChild(button);
    div.appendChild(detailsDiv);
    div.appendChild(updateButton);
    div.appendChild(deleteButton);

    return div;
}

// Buton oluşturma fonksiyonu
function createButton(text, className, clickHandler) {
    const button = document.createElement('button');
    button.textContent = text;
    button.className = className;
    button.addEventListener('click', clickHandler);
    return button;
}

// Kanban başlığını yükleyen fonksiyon
async function loadKanbans() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/projects/${kanbanId}`);
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');
        }
        const kanban = await response.json();
        document.getElementById('kanban-title').textContent = kanban.kanbanName || 'KANBAN';
    } catch (error) {
        console.error('Kanban bilgileri yüklenirken bir hata oluştu:', error);
    }
}

// Kullanıcı bilgilerini yükleyen fonksiyon
async function loadUsers() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`);
        if (!response.ok) {
            throw new Error('Ağ yanıtı uygun değil');
        }
        const data = await response.json();
        const userList = document.getElementById('username');
        if (userList) {
            userList.innerHTML = '';
            const div = document.createElement('div');
            div.textContent = data.userName;
            userList.appendChild(div);
        } else {
            console.error('Kullanıcı liste öğesi bulunamadı');
        }
    } catch (error) {
        console.error('Kullanıcı bilgileri yüklenirken bir hata oluştu:', error);
    }
}

// Update modal ve form işlemleri
document.addEventListener('DOMContentLoaded', () => {
    const updateTaskModal = document.getElementById('update-task-modal');
    const closeUpdateModal = document.getElementById('close-update-modal');
    const updateTaskForm = document.getElementById('update-task-form');

    // Update modal'ı kapama işlevi
    closeUpdateModal.addEventListener('click', () => {
        updateTaskModal.style.display = 'none';
    });

    // Modal dışında tıklama ile kapatma işlevi
    window.addEventListener('click', (event) => {
        if (event.target === updateTaskModal) {
            updateTaskModal.style.display = 'none';
        }
    });

    // Görev güncelleme formu gönderimi
    updateTaskForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const taskId = document.getElementById('update-task-id').value;
        const taskName = document.getElementById('update-task-title').value;
        const statusId = document.getElementById('update-task-status').value;
        const taskDescription = document.getElementById('update-task-description').value;
        const assignedToUser = document.getElementById('update-task-assigned-user').value;

        try {
            const response = await fetch(`http://127.0.0.1:8000/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    taskName: taskName,
                    statusId: statusId,
                    taskDescription: taskDescription,
                    assignedToUser: assignedToUser
                })
            });

            if (response.ok) {
                alert('Görev başarıyla güncellendi!');
                updateTaskModal.style.display = 'none';
                loadTasks(); // Görevleri yeniden yükle
            } else {
                const error = await response.json();
                alert(`Hata: ${error.detail}`);
            }
        } catch (error) {
            alert(`Hata: ${error.message}`);
        }
    });

    // Yeni görev oluşturma modal'ını kontrol etme
    const createTaskBtn = document.getElementById('create-task-btn');
    const createTaskModal = document.getElementById('create-task-modal');
    const closeModal = document.getElementById('close-modal');
    const createTaskForm = document.getElementById('create-task-form');

    createTaskBtn.addEventListener('click', () => {
        createTaskModal.style.display = 'block';
    });

    closeModal.addEventListener('click', () => {
        createTaskModal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === createTaskModal) {
            createTaskModal.style.display = 'none';
        }
    });

    // Yeni görev oluşturma formu gönderimi
    createTaskForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const taskName = document.getElementById('task-title').value;
        const statusId = document.getElementById('task-status').value;
        const taskDescription = document.getElementById('task-description').value;
        const assignedToUser = document.getElementById('task-assigned-user').value;

        try {
            const response = await fetch('http://127.0.0.1:8000/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    taskName: taskName,
                    statusId: statusId,
                    kanbanId: kanbanId,
                    taskDescription: taskDescription,
                    assignedToUser: assignedToUser || 0,
                    taskCreatedAt: new Date().toISOString(),
                    taskUpdatedAt: new Date().toISOString()
                })
            });

            if (response.ok) {
                alert('Görev başarıyla oluşturuldu!');
                createTaskModal.style.display = 'none';
                createTaskForm.reset();
                loadTasks(); // Yeni oluşturulan görevi listeye ekle
            } else {
                const error = await response.json();
                alert(`Hata: ${error.detail}`);
            }
        } catch (error) {
            alert(`Hata: ${error.message}`);
        }
    });

    // Sayfa yüklendiğinde kullanıcıları, görevleri ve kanban'ı yükleyin
    loadUsers();
    loadTasks();
    loadKanbans();
});
