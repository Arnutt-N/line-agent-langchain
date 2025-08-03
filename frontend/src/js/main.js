// ===== Enhanced LINE Bot Admin Panel =====
// WebSocket & State Management
const ws = new WebSocket(`ws://${window.location.host}/ws`)
let selectedUser = null
const sound = new Audio("/notify.mp3")

// User Map for enhanced data management
const users = new Map()

// Initialize Profile Manager
let profileManager = null
let userComponents = new Map()

// Initialize CRUD and Message Manager
let crudManager = null
let messageManager = null

// Initialize Analytics Dashboard
let analyticsDashboard = null

// Initialize Chat History Manager
let chatHistoryManager = null

// ===== Theme System =====
const themes = ['light', 'dark', 'blue', 'green', 'purple']
let currentTheme = localStorage.getItem('theme') || 'light'

function initTheme() {
  document.documentElement.setAttribute('data-theme', currentTheme)
  updateThemeSelector()
}

function changeTheme(theme) {
  currentTheme = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
  updateThemeSelector()
}

function updateThemeSelector() {
  const selector = document.getElementById('theme-selector')
  if (selector) {
    selector.value = currentTheme
  }
}

// ===== Enhanced Profile Management =====
async function initializeProfileManager() {
  if (typeof UserProfileManager !== 'undefined') {
    profileManager = new UserProfileManager()
    
    // Auto cleanup cache every hour
    setInterval(() => {
      profileManager.cleanupCache()
    }, 3600000)
  }
}

// Enhanced user data structure
async function createEnhancedUser(userId, displayName, pictureUrl, additionalData = {}) {
  // Get profile from manager if available
  let profile = null
  if (profileManager) {
    profile = await profileManager.getProfile(userId)
  }
  
  return {
    id: userId,
    displayName: profile?.display_name || displayName || `Customer ${userId.slice(-6)}`,
    avatar: profile?.picture_url || pictureUrl || null,
    status_message: profile?.status_message || '',
    language: profile?.language || 'th',
    isOnline: true,
    is_in_live_chat: additionalData.is_in_live_chat || false,
    unreadCount: 0,
    status: 'กำลังแชท',
    chatEnded: false,
    chatMode: additionalData.chat_mode || 'bot',
    lastActivity: new Date().toISOString(),
    sessionId: `session_${userId}_${new Date().toISOString().split('T')[0]}`,
    lastMessage: additionalData.lastMessage || '',
    profileSource: profile?.source || 'local'
  }
}

// ===== WebSocket Message Handler =====
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('WebSocket message received:', data)
  
  switch(data.type) {
    case "new_message":
    case "message":
      handleNewMessage(data)
      break
    case "new_user_request":
    case "new_user":
      handleNewUser(data)
      break
    case "profile_update":
      updateUserProfile(data)
      break
    case "status_update":
      updateUserStatus(data)
      break
    case "user_update":
      loadUsers()
      loadDashboard()
      break
    case "mode_switch":
      handleModeSwitch(data)
      break
    case "typing":
      showTypingIndicator(data.userId, data.isTyping)
      break
  }
}

// ===== Message Handlers =====
async function handleNewMessage(data) {
  // Update or create user with enhanced profile
  if (data.userId) {
    await addOrUpdateUser(data.userId, data.displayName, data.pictureUrl, {
      ...data,
      lastMessage: data.text || data.message
    })
  }
  
  // Display message if this user is selected
  if (data.user_id === selectedUser || data.userId === selectedUser) {
    appendMessage(data.text || data.message, data.from === "user" || data.sender_type === "user", data)
  }
  
  // Update unread count
  if (data.userId && data.userId !== selectedUser) {
    const user = users.get(data.userId)
    if (user) {
      user.unreadCount = (user.unreadCount || 0) + 1
      user.lastMessage = data.text || data.message
      updateUsersList()
    }
  }
  
  // Notifications
  if (document.getElementById("desktop-notify")?.checked) {
    new Notification(`New message from ${data.displayName || data.user_id}`, {
      body: data.text || data.message,
      icon: data.pictureUrl
    })
  }
  if (document.getElementById("sound-notify")?.checked) {
    sound.play()
  }
}

async function handleNewUser(data) {
  await addOrUpdateUser(data.userId, data.displayName, data.pictureUrl, data)
  updateUsersList()
}

async function updateUserProfile(data) {
  const user = users.get(data.userId)
  if (user) {
    // Update local data
    user.displayName = data.displayName || user.displayName
    user.avatar = data.pictureUrl || user.avatar
    user.status_message = data.status_message || user.status_message
    
    // Update profile manager cache
    if (profileManager) {
      profileManager.updateProfile(data.userId, {
        display_name: data.displayName,
        picture_url: data.pictureUrl,
        status_message: data.status_message
      })
    }
    
    // Update UI
    const component = userComponents.get(data.userId)
    if (component) {
      component.update(user)
      component.animateUpdate()
    } else {
      updateUsersList()
    }
  }
}

function updateUserStatus(data) {
  const user = users.get(data.userId)
  if (user) {
    user.isOnline = data.isOnline
    user.status = data.status
    user.lastActivity = data.timestamp
    
    const component = userComponents.get(data.userId)
    if (component) {
      component.update(user)
    } else {
      updateUsersList()
    }
  }
}

function handleModeSwitch(data) {
  const user = users.get(data.user_id || data.userId)
  if (user) {
    user.chatMode = data.mode
    
    const component = userComponents.get(data.user_id || data.userId)
    if (component) {
      component.update(user)
    } else {
      updateUsersList()
    }
  }
  
  // Update mode buttons if this user is selected
  if ((data.user_id || data.userId) === selectedUser) {
    updateModeButtons(data.mode)
  }
}

// ===== User Management =====
async function addOrUpdateUser(userId, displayName, pictureUrl, additionalData = {}) {
  if (!users.has(userId)) {
    const enhancedUser = await createEnhancedUser(userId, displayName, pictureUrl, additionalData)
    users.set(userId, enhancedUser)
  } else {
    const user = users.get(userId)
    user.displayName = displayName || user.displayName
    user.avatar = pictureUrl || user.avatar
    user.lastActivity = new Date().toISOString()
    Object.assign(user, additionalData)
    
    // Update component if exists
    const component = userComponents.get(userId)
    if (component) {
      component.update(user)
    }
  }
}

// ===== Enhanced User List Display =====
function updateUsersList() {
  const usersList = document.getElementById('user-list')
  if (!usersList) return
  
  // Clear existing components
  userComponents.clear()
  usersList.innerHTML = ''
  
  // Sort users by last activity
  const sortedUsers = Array.from(users.values()).sort((a, b) => 
    new Date(b.lastActivity) - new Date(a.lastActivity)
  )
  
  // Apply filters
  const statusFilter = document.getElementById('status-filter')?.value || 'all'
  const modeFilter = document.getElementById('mode-filter')?.value || 'all'
  
  const filteredUsers = sortedUsers.filter(user => {
    if (statusFilter === 'online' && !user.isOnline) return false
    if (statusFilter === 'offline' && user.isOnline) return false
    if (statusFilter === 'unread' && !user.unreadCount) return false
    
    if (modeFilter !== 'all' && user.chatMode !== modeFilter) return false
    
    return true
  })
  
  // Create components
  filteredUsers.forEach(user => {
    if (typeof UserComponent !== 'undefined') {
      const component = new UserComponent(user, profileManager)
      const element = component.createElement()
      usersList.appendChild(element)
      userComponents.set(user.id, component)
    } else {
      // Fallback to old rendering
      const userDiv = createBasicUserElement(user)
      usersList.appendChild(userDiv)
    }
  })
  
  // Update online count
  const onlineCount = sortedUsers.filter(u => u.isOnline).length
  const onlineCountEl = document.getElementById('online-count')
  if (onlineCountEl) {
    onlineCountEl.textContent = `${onlineCount} online`
  }
  
  // Update stats
  updateQuickStats()
}

// Fallback user element creation
function createBasicUserElement(user) {
  const userDiv = document.createElement('div')
  userDiv.className = `user-item ${user.id === selectedUser ? 'active' : ''} animate-slideIn`
  
  const avatarContent = user.avatar 
    ? `<img src="${user.avatar}" alt="${user.displayName}" onerror="this.src='/default-avatar.png'">` 
    : `<span>${user.displayName.charAt(0).toUpperCase()}</span>`
  
  userDiv.innerHTML = `
    <div class="user-avatar">
      ${avatarContent}
      <div class="online-indicator ${user.isOnline ? 'online' : 'offline'}"></div>
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <div class="user-name font-medium">${user.displayName}</div>
        ${user.unreadCount > 0 ? `<div class="unread-count">${user.unreadCount}</div>` : ''}
      </div>
      <div class="flex items-center justify-between text-xs">
        <div class="user-status">${user.status}</div>
        <div class="chat-mode-badge ${user.chatMode}">
          ${user.chatMode === 'bot' ? '🤖' : '👤'} ${user.chatMode}
        </div>
      </div>
    </div>
  `
  
  userDiv.addEventListener('click', () => selectUser(user.id, user.displayName))
  return userDiv
}

// Update quick stats
function updateQuickStats() {
  const totalMessages = Array.from(users.values()).reduce((sum, user) => sum + (user.messageCount || 0), 0)
  const activeChats = Array.from(users.values()).filter(u => u.is_in_live_chat).length
  
  document.getElementById('stat-messages-today').textContent = totalMessages
  document.getElementById('stat-active-chats').textContent = activeChats
}

// Continue with rest of the code...

// ===== Load Users from API =====
async function loadUsers() {
  try {
    const res = await fetch("/api/users")
    const apiUsers = await res.json()
    
    // Process each user with profile enhancement
    for (const user of apiUsers) {
      await addOrUpdateUser(
        user.line_id,
        user.name,
        user.picture,
        {
          chat_mode: user.mode,
          is_in_live_chat: user.is_in_live_chat
        }
      )
    }
    
    updateUsersList()
  } catch (error) {
    console.error('Error loading users:', error)
  }
}

// ===== Enhanced Dashboard =====
async function loadDashboard() {
  try {
    const res = await fetch("/api/dashboard")
    const stats = await res.json()
    const dashboard = document.getElementById("dashboard")
    
    dashboard.innerHTML = `
      <div class="stat-card">
        <div class="flex items-center justify-between mb-2">
          <i data-lucide="users" class="w-8 h-8 text-blue-500"></i>
          <span class="text-xs text-gray-500">Total</span>
        </div>
        <div class="text-2xl font-bold">${stats.total_users}</div>
        <div class="text-sm text-gray-600">Total Users</div>
      </div>
      
      <div class="stat-card">
        <div class="flex items-center justify-between mb-2">
          <i data-lucide="user-plus" class="w-8 h-8 text-green-500"></i>
          <span class="text-xs text-gray-500">Today</span>
        </div>
        <div class="text-2xl font-bold">${stats.daily_adds}</div>
        <div class="text-sm text-gray-600">New Users</div>
      </div>
      
      <div class="stat-card">
        <div class="flex items-center justify-between mb-2">
          <i data-lucide="message-square" class="w-8 h-8 text-purple-500"></i>
          <span class="text-xs text-gray-500">Active</span>
        </div>
        <div class="text-2xl font-bold">${users.size}</div>
        <div class="text-sm text-gray-600">Active Chats</div>
      </div>
      
      <div class="stat-card">
        <div class="flex items-center justify-between mb-2">
          <i data-lucide="activity" class="w-8 h-8 text-orange-500"></i>
          <span class="text-xs text-gray-500">Status</span>
        </div>
        <div class="text-2xl font-bold text-green-500">Online</div>
        <div class="text-sm text-gray-600">System Status</div>
      </div>
    `
    lucide.createIcons()
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
}

// ===== User Selection =====
function selectUser(userId, userName) {
  selectedUser = userId
  const user = users.get(userId)
  
  // Mark messages as read
  if (user) {
    user.unreadCount = 0
    const component = userComponents.get(userId)
    if (component) {
      component.update(user)
    }
  }
  
  // Update UI
  document.getElementById("dashboard").classList.add("hidden")
  document.getElementById("chat-window").classList.remove("hidden")
  document.getElementById("chat-title").textContent = userName
  document.getElementById("main-title").textContent = userName
  
  // Update chat header with avatar
  if (user && user.avatar) {
    const avatarEl = document.getElementById("chat-user-avatar")
    if (avatarEl) {
      avatarEl.src = user.avatar
      avatarEl.style.display = 'block'
    }
  }
  
  // Update chat status
  const statusEl = document.getElementById("chat-status")
  if (statusEl && user) {
    statusEl.textContent = user.status_message || user.status
  }
  
  cleanupControls()
  loadChatHistory(userId)
  addModeControls(userId)
  
  // Show message toolbar if available
  if (messageManager) {
    messageManager.showToolbar()
  }
  
  if (typeof addLoadingControls === 'function') {
    addLoadingControls()
  }
}

// ===== Control Functions =====
function cleanupControls() {
  const existingModeControls = document.getElementById('mode-controls')
  const existingLoadingControls = document.getElementById('loading-controls')
  
  if (existingModeControls) existingModeControls.remove()
  if (existingLoadingControls) existingLoadingControls.remove()
}

async function addModeControls(userId) {
  const chatActions = document.querySelector('.chat-actions')
  if (chatActions && !document.getElementById('mode-controls')) {
    const user = users.get(userId)
    const currentMode = user?.chatMode || 'bot'
    
    const modeControls = document.createElement('div')
    modeControls.id = 'mode-controls'
    modeControls.className = 'flex gap-2 mb-2'
    modeControls.innerHTML = `
      <button id="mode-manual" class="btn-mode ${currentMode === 'manual' ? 'active' : ''}" 
              onclick="switchMode('${userId}', 'manual')">
        <i data-lucide="user" class="w-4 h-4 mr-1"></i> Manual Mode
      </button>
      <button id="mode-bot" class="btn-mode ${currentMode === 'bot' ? 'active' : ''}" 
              onclick="switchMode('${userId}', 'bot')">
        <i data-lucide="bot" class="w-4 h-4 mr-1"></i> Bot Mode
      </button>
    `
    
    chatActions.insertBefore(modeControls, chatActions.firstChild)
    lucide.createIcons()
  }
}

function updateModeButtons(mode) {
  document.querySelectorAll('.btn-mode').forEach(btn => {
    btn.classList.remove('active')
  })
  
  if (mode === 'manual') {
    document.getElementById('mode-manual')?.classList.add('active')
  } else {
    document.getElementById('mode-bot')?.classList.add('active')
  }
}

async function switchMode(userId, mode) {
  try {
    const res = await fetch(`/api/users/${userId}/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode })
    })
    
    if (res.ok) {
      updateModeButtons(mode)
      const user = users.get(userId)
      if (user) {
        user.chatMode = mode
        const component = userComponents.get(userId)
        if (component) {
          component.update(user)
        }
      }
    }
  } catch (error) {
    console.error('Error switching mode:', error)
  }
}

// ===== Chat Functions =====
async function loadChatHistory(userId) {
  const messagesDiv = document.getElementById("chat-messages")
  messagesDiv.innerHTML = '<div class="text-center text-gray-500">Loading messages...</div>'
  
  // Use MessageManager if available
  if (messageManager) {
    await messageManager.loadMessages(userId)
    return
  }
  
  // Fallback to original implementation
  try {
    const res = await fetch(`/api/users/${userId}/messages`)
    const messages = await res.json()
    
    messagesDiv.innerHTML = ""
    messages.forEach(msg => {
      appendMessage(msg.text, msg.from === "user", msg)
    })
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight
  } catch (error) {
    messagesDiv.innerHTML = '<div class="text-center text-red-500">Error loading messages</div>'
    console.error('Error loading chat history:', error)
  }
}

function appendMessage(text, isUser, data = {}) {
  const messagesDiv = document.getElementById("chat-messages")
  const messageDiv = document.createElement("div")
  messageDiv.className = `message ${isUser ? 'user' : data.sender_type || 'bot'} animate-fadeIn`
  
  // Add timestamp
  const timestamp = new Date(data.timestamp || new Date()).toLocaleTimeString('th-TH', {
    hour: '2-digit',
    minute: '2-digit'
  })
  
  // Show timestamps based on setting
  const showTimestamps = document.getElementById('show-timestamps')?.checked !== false
  
  messageDiv.innerHTML = `
    <div class="message-content">${text}</div>
    ${showTimestamps ? `<div class="text-xs opacity-70 mt-1">${timestamp}</div>` : ''}
  `
  
  messagesDiv.appendChild(messageDiv)
  messagesDiv.scrollTop = messagesDiv.scrollHeight
}

// ===== Typing Indicator =====
function showTypingIndicator(userId, isTyping) {
  if (userId !== selectedUser) return
  
  const messagesDiv = document.getElementById("chat-messages")
  let indicator = document.getElementById("typing-indicator")
  
  if (isTyping && !indicator) {
    indicator = document.createElement("div")
    indicator.id = "typing-indicator"
    indicator.className = "typing-indicator animate-fadeIn"
    indicator.innerHTML = `
      <div class="typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
      <span class="typing-text">AI กำลังพิมพ์...</span>
    `
    messagesDiv.appendChild(indicator)
    messagesDiv.scrollTop = messagesDiv.scrollHeight
  } else if (!isTyping && indicator) {
    indicator.remove()
  }
}

// ===== Form Handling =====
document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
  e.preventDefault()
  const input = document.getElementById("chat-input")
  const message = input.value.trim()
  
  if (!message || !selectedUser) return
  
  // Show message immediately
  appendMessage(message, false, { sender_type: 'admin', timestamp: new Date() })
  
  try {
    const res = await fetch(`/api/users/${selectedUser}/reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    })
    
    if (!res.ok) {
      throw new Error('Failed to send message')
    }
    
    input.value = ""
  } catch (error) {
    console.error('Error sending message:', error)
    appendMessage('Error sending message. Please try again.', false, { sender_type: 'system' })
  }
})

// ===== Theme Selector =====
function createThemeSelector() {
  const settingsDiv = document.querySelector('aside:last-child')
  if (settingsDiv && !document.getElementById('theme-selector-container')) {
    const themeContainer = document.createElement('div')
    themeContainer.id = 'theme-selector-container'
    themeContainer.className = 'mb-4'
    themeContainer.innerHTML = `
      <h3 class="text-sm font-medium mb-2">Theme</h3>
      <select id="theme-selector" class="w-full p-2 rounded border" onchange="changeTheme(this.value)">
        <option value="light">☀️ Light</option>
        <option value="dark">🌙 Dark</option>
        <option value="blue">💙 Blue</option>
        <option value="green">💚 Green</option>
        <option value="purple">💜 Purple</option>
      </select>
    `
    settingsDiv.insertBefore(themeContainer, settingsDiv.children[1])
  }
}

// ===== Search Functionality =====
function createSearchBox() {
  const userListHeader = document.querySelector('aside:first-child h3')
  if (userListHeader && !document.getElementById('user-search-container')) {
    const searchContainer = document.createElement('div')
    searchContainer.id = 'user-search-container'
    searchContainer.className = 'search-box mb-4'
    searchContainer.innerHTML = `
      <i data-lucide="search" class="w-4 h-4"></i>
      <input type="text" id="user-search" placeholder="ค้นหาผู้ใช้..." 
             oninput="filterUsers(this.value)" />
    `
    userListHeader.parentNode.insertBefore(searchContainer, userListHeader.nextSibling)
    lucide.createIcons()
  }
}

function filterUsers(searchTerm) {
  const term = searchTerm.toLowerCase()
  
  userComponents.forEach((component, userId) => {
    const user = users.get(userId)
    const userName = user.displayName.toLowerCase()
    const matchesSearch = !term || userName.includes(term)
    
    if (component.element) {
      component.element.style.display = matchesSearch ? '' : 'none'
    }
  })
}

// ===== Keyboard Shortcuts =====
document.addEventListener('keydown', (e) => {
  // Ctrl+B: Toggle Sidebar
  if (e.ctrlKey && e.key === 'b') {
    e.preventDefault()
    document.querySelector('aside:first-child').classList.toggle('hidden')
  }
  
  // Ctrl+F: Focus Search
  if (e.ctrlKey && e.key === 'f') {
    e.preventDefault()
    document.getElementById('user-search')?.focus()
  }
  
  // Ctrl+D: Toggle Theme
  if (e.ctrlKey && e.key === 'd') {
    e.preventDefault()
    const themes = ['light', 'dark', 'blue', 'green', 'purple']
    const currentIndex = themes.indexOf(currentTheme)
    const nextTheme = themes[(currentIndex + 1) % themes.length]
    changeTheme(nextTheme)
  }
})

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', async () => {
  initTheme()
  createThemeSelector()
  createSearchBox()
  
  // Initialize profile manager
  await initializeProfileManager()
  
  // Initialize CRUD and Message Manager
  if (typeof CRUDManager !== 'undefined') {
    crudManager = new CRUDManager()
  }
  
  if (typeof MessageManager !== 'undefined' && crudManager) {
    messageManager = new MessageManager(crudManager)
    messageManager.initializeUI()
  }
  
  // Initialize Analytics Dashboard
  if (typeof AnalyticsDashboard !== 'undefined') {
    analyticsDashboard = new AnalyticsDashboard()
  }
  
  // Initialize Chat History Manager
  if (typeof ChatHistoryManager !== 'undefined' && crudManager) {
    chatHistoryManager = new ChatHistoryManager(crudManager)
    chatHistoryManager.initializeUI()
  }
  
  // Load initial data
  await loadUsers()
  loadDashboard()
  
  // Check notification permission
  if (Notification.permission === 'default') {
    Notification.requestPermission()
  }
  
  // Refresh data every 30 seconds
  setInterval(() => {
    loadUsers()
    loadDashboard()
  }, 30000)
})

// Export functions for use in other modules
window.switchMode = switchMode
window.changeTheme = changeTheme
window.filterUsers = filterUsers
window.applyFilters = () => updateUsersList()
