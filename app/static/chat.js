function showContent(type) {
    const text = {
        order: `
        <h2>📦 Track Your Order</h2>
        <p>Enter your order ID to see real-time status.</p>
        <ul>
            <li>Current location</li>
            <li>Estimated delivery</li>
            <li>Delay alerts</li>
        </ul>`,

        return: `
        <h2>🔄 Returns & Refunds</h2>
        <p>Return products within 30 days.</p>
        <ul>
            <li>Pickup scheduling</li>
            <li>Refund tracking</li>
            <li>Status updates</li>
        </ul>`,

        shipping: `
        <h2>🚚 Shipping Information</h2>
        <ul>
            <li>Standard & Express</li>
            <li>Live tracking</li>
        </ul>`,

        payment: `
        <h2>💳 Payment Issues</h2>
        <ul>
            <li>Failed payments</li>
            <li>Duplicate charges</li>
            <li>Billing help</li>
        </ul>`,

        account: `
        <h2>👤 Account Help</h2>
        <ul>
            <li>Reset password</li>
            <li>Update address</li>
            <li>Privacy & security</li>
        </ul>`
    };

    document.getElementById("mainContent").classList.remove("hidden");
    document.getElementById("chatPanel").style.display = "none";
    document.getElementById("dummyText").innerHTML = text[type];
}

function openChat() {
    document.getElementById("mainContent").classList.add("hidden");
    document.getElementById("chatPanel").style.display = "flex";
}

function closeChat() {
    document.getElementById("mainContent").classList.remove("hidden");
    document.getElementById("chatPanel").style.display = "none";
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="user-msg">${message}</div>`;
    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    chatBox.innerHTML += `<div class="bot-msg">${data.response}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("user-input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});
