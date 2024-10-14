document.addEventListener("DOMContentLoaded", () => {
    // Login formunu işleme
    const loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", handleLogin);
});

// Login işlemini yapan asenkron fonksiyon
async function handleLogin(event) {
    event.preventDefault();

    // Form verilerini al
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await performLogin(email, password);

        if (response.ok) {
            const data = await response.json();
            handleLoginSuccess(data.userId);
        } else {
            const errorData = await response.json();
            handleLoginError(errorData.detail);
        }
    } catch (error) {
        handleError(error);
    }
}

// Login isteğini gerçekleştiren fonksiyon
async function performLogin(email, password) {
    return fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            userEmail: email,
            userPasswordHashed: password
        })
    });
}

// Başarıyla giriş yapılınca yapılan işlemler
function handleLoginSuccess(userId) {
    alert('Giriş başarılı!');
    window.location.href = `/app/templates/profil.html?userId=${userId}`;
}

// Giriş hatası durumunda yapılan işlemler
function handleLoginError(errorDetail) {
    alert(`Giriş başarısız: ${errorDetail}`);
}

// Genel hata durumunda yapılan işlemler
function handleError(error) {
    console.error("Hata:", error);
    alert("Bir hata oluştu. Lütfen tekrar deneyin.");
}
