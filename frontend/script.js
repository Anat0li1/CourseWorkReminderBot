const tg = window.Telegram.WebApp;
tg.expand();  // Розгортає WebApp на весь екран

const backendUrl = "https://1e74-194-44-82-106.ngrok-free.app/miniapp"; // Замінити на твій бекенд

// Отримуємо user_id з initData (перевіряємо підписаний токен)
let userData = new URLSearchParams(tg.initData);
let userId = userData.get("user") ? JSON.parse(userData.get("user")).id : null;

if (!userId) {
    alert("Помилка авторизації!");
} else {
    fetch(`${backendUrl}/get_reminder?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("reminder-date").value = data.date || "";
            document.getElementById("description").value = data.description || "";

            if (data.has_subscription) {
                document.getElementById("repeat").value = data.repeat;
                document.getElementById("repeat-container").style.display = "block";
            }
        });
}

document.getElementById("save-btn").addEventListener("click", () => {
    fetch(`${backendUrl}/save_reminder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            date: document.getElementById("reminder-date").value,
            repeat: document.getElementById("repeat").value,
            description: document.getElementById("description").value,
        }),
    }).then(() => tg.close());  // Закриває Mini App
});
