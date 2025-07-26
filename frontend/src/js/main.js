const ws = new WebSocket(`ws://${window.location.host}/ws`)
let selectedUser = null
const sound = new Audio("/notify.mp3")

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === "message") {
    if (data.user_id === selectedUser) {
      appendMessage(data.text, data.from === "user")
    }
    if (document.getElementById("desktop-notify").checked) {
      new Notification(`New message from ${data.user_id}`)
    }
    if (document.getElementById("sound-notify").checked) {
      sound.play()
    }
  } else if (data.type === "user_update" || data.type === "mode_switch") {
    loadUsers()
  }
}

async function loadUsers() {
  const res = await fetch("/api/users")
  const users = await res.json()
  const list = document.getElementById("user-list")
  list.innerHTML = ""
  users.forEach((user) => {
    const li = document.createElement("li")
    li.className =
      "flex items-center p-2 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
    li.innerHTML = `<img src="${
      user.picture || ""
    }" class="w-8 h-8 rounded-full mr-2"> ${user.name} <span class="ml-auto">${
      user.mode
    }</span>`
    li.onclick = () => selectUser(user.line_id, user.name)
    list.appendChild(li)
  })
}

async function loadDashboard() {
  const res = await fetch("/api/dashboard")
  const stats = await res.json()
  const dashboard = document.getElementById("dashboard")
  dashboard.innerHTML = `
    <div class="p-4 bg-blue-100 dark:bg-blue-800 rounded"><i data-lucide="users"></i> Total Users: ${stats.total_users}</div>
    <div class="p-4 bg-green-100 dark:bg-green-800 rounded"><i data-lucide="user-plus"></i> Daily Adds: ${stats.daily_adds}</div>
    <div class="p-4 bg-red-100 dark:bg-red-800 rounded"><i data-lucide="user-minus"></i> Daily Blocks: ${stats.daily_blocks}</div>
    <div class="p-4 bg-yellow-100 dark:bg-yellow-800 rounded"><i data-lucide="refresh-cw"></i> Daily Renews: ${stats.daily_renews}</div>
  `
  lucide.createIcons()
}

function selectUser(userId, userName) {
  selectedUser = userId
  document.getElementById("dashboard").classList.add("hidden")
  document.getElementById("chat-window").classList.remove("hidden")
  document.getElementById("chat-title").textContent = userName
  loadChatHistory(userId)
}

async function loadChatHistory(userId) {
  const res = await fetch(`/api/users/${userId}/chat`)
  const messages = await res.json()
  const chatDiv = document.getElementById("chat-messages")
  chatDiv.innerHTML = ""
  messages.forEach((msg) => {
    appendMessage(msg.message, msg.is_from_user)
  })
}

function appendMessage(text, isFromUser) {
  const chatDiv = document.getElementById("chat-messages")
  const msgDiv = document.createElement("div")
  msgDiv.className = `mb-2 ${isFromUser ? "text-right" : "text-left"}`
  msgDiv.innerHTML = `<span class="inline-block p-2 rounded ${
    isFromUser ? "bg-blue-500 text-white" : "bg-gray-300"
  }">${text}</span>`
  chatDiv.appendChild(msgDiv)
  chatDiv.scrollTop = chatDiv.scrollHeight
}

loadUsers()
loadDashboard()

// Export for use in other modules
window.appendMessage = appendMessage
window.selectedUser = () => selectedUser