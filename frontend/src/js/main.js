const ws = new WebSocket(`ws://${window.location.host}/ws`)
let selectedUser = null
const sound = new Audio("/notify.mp3")

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('WebSocket message received:', data)
  
  if (data.type === "message") {
    if (data.user_id === selectedUser) {
      appendMessage(data.text, data.from === "user")
    }
    // Show notification for new messages
    if (document.getElementById("desktop-notify").checked) {
      new Notification(`New message from ${data.user_id}`)
    }
    if (document.getElementById("sound-notify").checked) {
      sound.play()
    }
  } else if (data.type === "user_update") {
    loadUsers()
    loadDashboard()
  } else if (data.type === "mode_switch") {
    loadUsers()
    // Update mode buttons if this user is currently selected
    if (data.user_id === selectedUser) {
      updateModeButtons(data.mode)
    }
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
  
  // Clean up existing controls
  cleanupControls()
  
  loadChatHistory(userId)
  
  // Add mode controls and loading controls
  addModeControls(userId)
  if (typeof addLoadingControls === 'function') {
    addLoadingControls()
  }
}

function cleanupControls() {
  // Remove existing controls
  const existingModeControls = document.getElementById('mode-controls')
  const existingLoadingControls = document.getElementById('loading-controls')
  
  if (existingModeControls) {
    existingModeControls.remove()
  }
  if (existingLoadingControls) {
    existingLoadingControls.remove()
  }
}

// Add mode control buttons
async function addModeControls(userId) {
  const chatActions = document.querySelector('.chat-actions')
  if (chatActions && !document.getElementById('mode-controls')) {
    // Get current user mode
    const users = await fetch("/api/users").then(res => res.json())
    const currentUser = users.find(u => u.line_id === userId)
    const currentMode = currentUser ? currentUser.mode : 'bot'
    
    const modeControls = document.createElement('div')
    modeControls.id = 'mode-controls'
    modeControls.className = 'flex gap-2 mb-2 items-center'
    modeControls.innerHTML = `
      <span class="text-sm font-medium">Mode:</span>
      <button id="bot-mode-btn" class="px-3 py-1 rounded text-sm ${currentMode === 'bot' ? 'bg-green-500 text-white' : 'bg-gray-300'}">
        <i data-lucide="bot"></i> Bot Mode
      </button>
      <button id="manual-mode-btn" class="px-3 py-1 rounded text-sm ${currentMode === 'manual' ? 'bg-blue-500 text-white' : 'bg-gray-300'}">
        <i data-lucide="user"></i> Manual Mode
      </button>
      <span id="current-mode" class="text-xs text-gray-500">(Current: ${currentMode})</span>
    `
    
    // Insert before form
    chatActions.insertBefore(modeControls, chatActions.firstChild)
    
    // Add event listeners
    document.getElementById('bot-mode-btn').addEventListener('click', () => {
      setUserMode(userId, 'bot')
    })
    
    document.getElementById('manual-mode-btn').addEventListener('click', () => {
      setUserMode(userId, 'manual')
    })
    
    // Initialize icons
    lucide.createIcons()
  }
}

// Set user mode
async function setUserMode(userId, mode) {
  try {
    const response = await fetch(`/api/mode/${userId}?mode=${mode}`, {
      method: 'POST'
    })
    const result = await response.json()
    
    if (result.status === 'ok') {
      // Update button states
      updateModeButtons(mode)
      console.log(`Mode changed to ${mode} for user ${userId}`)
    } else {
      console.error('Failed to change mode:', result)
    }
  } catch (error) {
    console.error('Error changing mode:', error)
  }
}

// Update mode button states
function updateModeButtons(mode) {
  const botBtn = document.getElementById('bot-mode-btn')
  const manualBtn = document.getElementById('manual-mode-btn')
  const currentModeSpan = document.getElementById('current-mode')
  
  if (botBtn && manualBtn && currentModeSpan) {
    // Reset button styles
    botBtn.className = `px-3 py-1 rounded text-sm ${mode === 'bot' ? 'bg-green-500 text-white' : 'bg-gray-300'}`
    manualBtn.className = `px-3 py-1 rounded text-sm ${mode === 'manual' ? 'bg-blue-500 text-white' : 'bg-gray-300'}`
    currentModeSpan.textContent = `(Current: ${mode})`
  }
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
window.setUserMode = setUserMode
window.updateModeButtons = updateModeButtons
window.addModeControls = addModeControls