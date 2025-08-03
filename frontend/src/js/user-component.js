// ===== Enhanced User Component =====
// Real-time user profile display component

class UserComponent {
  constructor(user, profileManager) {
    this.user = user
    this.profileManager = profileManager
    this.element = null
    this.lastActivity = new Date(user.lastActivity || new Date())
  }

  // สร้าง HTML element
  createElement() {
    const div = document.createElement('div')
    div.className = `user-item ${this.user.id === selectedUser ? 'active' : ''} animate-slideIn`
    div.id = `user-${this.user.id}`
    
    div.innerHTML = this.getHTML()
    div.addEventListener('click', () => this.handleClick())
    
    this.element = div
    return div
  }

  // Generate HTML
  getHTML() {
    const avatar = this.getAvatarHTML()
    const status = this.getStatusHTML()
    const activity = this.getActivityTime()
    
    return `
      <div class="flex items-center p-3">
        <div class="user-avatar relative">
          ${avatar}
          <div class="online-indicator ${this.user.isOnline ? 'online' : 'offline'}"></div>
        </div>
        
        <div class="flex-1 ml-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="user-name font-medium text-sm">${this.user.displayName}</div>
              ${status}
            </div>
            <div class="text-right">
              ${this.getUnreadBadge()}
              <div class="text-xs text-gray-500">${activity}</div>
            </div>
          </div>
          
          <div class="flex items-center mt-1">
            ${this.getChatModeBadge()}
            ${this.getLastMessagePreview()}
          </div>
        </div>
      </div>
    `
  }

  // Avatar with multiple fallbacks
  getAvatarHTML() {
    if (this.user.avatar) {
      return `
        <img src="${this.user.avatar}" 
             alt="${this.user.displayName}" 
             onerror="this.onerror=null; this.src='${this.profileManager.defaultAvatar}';"
             class="w-12 h-12 rounded-full object-cover">
      `
    }
    
    // Letter avatar fallback
    const initial = this.user.displayName.charAt(0).toUpperCase()
    const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500']
    const colorIndex = this.user.id.charCodeAt(0) % colors.length
    
    return `
      <div class="w-12 h-12 rounded-full ${colors[colorIndex]} flex items-center justify-center text-white font-semibold">
        ${initial}
      </div>
    `
  }

  // Status message or default status
  getStatusHTML() {
    if (this.user.status_message) {
      return `<div class="text-xs text-gray-600 truncate max-w-[150px]">${this.user.status_message}</div>`
    }
    
    const status = this.user.is_in_live_chat ? 'กำลังคุยกับ Admin' : this.user.status
    return `<div class="text-xs text-gray-500">${status}</div>`
  }

  // Chat mode badge
  getChatModeBadge() {
    const mode = this.user.chatMode || 'bot'
    const icon = mode === 'bot' ? '🤖' : '👤'
    const color = mode === 'bot' ? 'blue' : 'green'
    
    return `
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-${color}-100 text-${color}-800">
        ${icon} ${mode}
      </span>
    `
  }

  // Unread message badge
  getUnreadBadge() {
    if (!this.user.unreadCount || this.user.unreadCount === 0) return ''
    
    return `
      <span class="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
        ${this.user.unreadCount > 9 ? '9+' : this.user.unreadCount}
      </span>
    `
  }

  // Last message preview
  getLastMessagePreview() {
    if (!this.user.lastMessage) return ''
    
    const maxLength = 30
    const preview = this.user.lastMessage.length > maxLength 
      ? this.user.lastMessage.substring(0, maxLength) + '...'
      : this.user.lastMessage
    
    return `<div class="text-xs text-gray-600 ml-2 flex-1 truncate">${preview}</div>`
  }

  // Activity time formatting
  getActivityTime() {
    const now = new Date()
    const diff = now - this.lastActivity
    
    if (diff < 60000) return 'ตอนนี้'
    if (diff < 3600000) return `${Math.floor(diff / 60000)} นาทีที่แล้ว`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} ชั่วโมงที่แล้ว`
    
    return this.lastActivity.toLocaleDateString('th-TH', {
      day: 'numeric',
      month: 'short'
    })
  }

  // Handle click event
  handleClick() {
    selectUser(this.user.id, this.user.displayName)
  }

  // Update component
  update(updates) {
    Object.assign(this.user, updates)
    if (this.element) {
      this.element.innerHTML = this.getHTML()
    }
  }

  // Animate update
  animateUpdate() {
    if (this.element) {
      this.element.classList.add('animate-pulse')
      setTimeout(() => {
        this.element.classList.remove('animate-pulse')
      }, 1000)
    }
  }
}

// Export
window.UserComponent = UserComponent
