// ===== CRUD Operations Module =====
// Enhanced data management with UI operations

class CRUDManager {
  constructor() {
    this.apiBase = '/api'
    this.cache = new Map()
    this.pendingOperations = new Set()
  }

  // ===== CREATE Operations =====
  
  // Create new message
  async createMessage(userId, content, type = 'admin') {
    const message = {
      id: this.generateId(),
      user_id: userId,
      message_type: type,
      message_content: content,
      timestamp: new Date().toISOString(),
      session_id: `session_${userId}_${new Date().toISOString().split('T')[0]}`
    }
    
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content })
      })
      
      if (!response.ok) throw new Error('Failed to send message')
      
      // Update local cache
      this.addToCache('messages', userId, message)
      
      return { success: true, data: message }
    } catch (error) {
      console.error('Create message error:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Create user note
  async createUserNote(userId, note) {
    const noteData = {
      id: this.generateId(),
      user_id: userId,
      note: note,
      created_by: 'admin',
      created_at: new Date().toISOString()
    }
    
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(noteData)
      })
      
      if (!response.ok) throw new Error('Failed to create note')
      
      return { success: true, data: noteData }
    } catch (error) {
      // Fallback to local storage
      this.saveToLocalStorage(`note_${userId}`, noteData)
      return { success: true, data: noteData, local: true }
    }
  }

  // ===== READ Operations =====
  
  // Read messages with pagination
  async readMessages(userId, options = {}) {
    const { limit = 50, offset = 0, search = '', dateFrom = null, dateTo = null } = options
    
    try {
      const params = new URLSearchParams({
        limit,
        offset,
        ...(search && { search }),
        ...(dateFrom && { date_from: dateFrom }),
        ...(dateTo && { date_to: dateTo })
      })
      
      const response = await fetch(`${this.apiBase}/users/${userId}/messages?${params}`)
      if (!response.ok) throw new Error('Failed to fetch messages')
      
      const data = await response.json()
      
      // Cache the results
      this.setCache('messages', userId, data.messages)
      
      return {
        success: true,
        data: data.messages,
        total: data.total,
        hasMore: data.has_more
      }
    } catch (error) {
      console.error('Read messages error:', error)
      
      // Try to get from cache
      const cached = this.getCache('messages', userId)
      if (cached) {
        return { success: true, data: cached, fromCache: true }
      }
      
      return { success: false, error: error.message }
    }
  }
  
  // Read user details
  async readUserDetails(userId) {
    const cacheKey = `user_${userId}`
    const cached = this.getCache('users', userId)
    
    if (cached && this.isCacheValid(cached)) {
      return { success: true, data: cached, fromCache: true }
    }
    
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}`)
      if (!response.ok) throw new Error('Failed to fetch user details')
      
      const data = await response.json()
      
      // Enrich with additional data
      data.notes = await this.readUserNotes(userId)
      data.stats = await this.readUserStats(userId)
      
      this.setCache('users', userId, data)
      
      return { success: true, data }
    } catch (error) {
      console.error('Read user error:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Read user notes
  async readUserNotes(userId) {
    // Try API first
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/notes`)
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      // Fallback to local storage
      const localNote = this.getFromLocalStorage(`note_${userId}`)
      return localNote ? [localNote] : []
    }
  }
  
  // Read user statistics
  async readUserStats(userId) {
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/stats`)
      if (!response.ok) throw new Error('Failed to fetch stats')
      
      return await response.json()
    } catch (error) {
      // Calculate from cached messages
      const messages = this.getCache('messages', userId) || []
      return this.calculateLocalStats(messages)
    }
  }

  // ===== UPDATE Operations =====
  
  // Update user status
  async updateUserStatus(userId, updates) {
    const updateData = {
      ...updates,
      updated_at: new Date().toISOString()
    }
    
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      })
      
      if (!response.ok) throw new Error('Failed to update user')
      
      // Update cache
      const cached = this.getCache('users', userId)
      if (cached) {
        this.setCache('users', userId, { ...cached, ...updateData })
      }
      
      return { success: true, data: updateData }
    } catch (error) {
      console.error('Update user error:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Update message (mark as read, edit, etc.)
  async updateMessage(messageId, updates) {
    try {
      const response = await fetch(`${this.apiBase}/messages/${messageId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      if (!response.ok) throw new Error('Failed to update message')
      
      return { success: true }
    } catch (error) {
      console.error('Update message error:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Bulk update messages (mark all as read)
  async bulkUpdateMessages(userId, updates) {
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/messages/bulk`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      if (!response.ok) throw new Error('Failed to bulk update')
      
      return { success: true }
    } catch (error) {
      console.error('Bulk update error:', error)
      return { success: false, error: error.message }
    }
  }

  // ===== DELETE Operations =====
  
  // Delete message (soft delete)
  async deleteMessage(messageId) {
    try {
      const response = await fetch(`${this.apiBase}/messages/${messageId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to delete message')
      
      return { success: true }
    } catch (error) {
      console.error('Delete message error:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Clear chat history
  async clearChatHistory(userId, confirm = false) {
    if (!confirm) {
      return { success: false, error: 'Confirmation required' }
    }
    
    try {
      const response = await fetch(`${this.apiBase}/users/${userId}/messages`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to clear history')
      
      // Clear cache
      this.clearCache('messages', userId)
      
      return { success: true }
    } catch (error) {
      console.error('Clear history error:', error)
      return { success: false, error: error.message }
    }
  }

  // ===== Utility Functions =====
  
  generateId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // Cache management
  setCache(type, key, data) {
    const cacheKey = `${type}_${key}`
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    })
  }
  
  getCache(type, key) {
    const cacheKey = `${type}_${key}`
    const cached = this.cache.get(cacheKey)
    return cached?.data
  }
  
  clearCache(type, key) {
    const cacheKey = `${type}_${key}`
    this.cache.delete(cacheKey)
  }
  
  isCacheValid(cached, maxAge = 300000) { // 5 minutes
    if (!cached.timestamp) return false
    return Date.now() - cached.timestamp < maxAge
  }
  
  addToCache(type, key, item) {
    const current = this.getCache(type, key) || []
    current.push(item)
    this.setCache(type, key, current)
  }
  
  // Local storage fallback
  saveToLocalStorage(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (e) {
      console.error('LocalStorage error:', e)
    }
  }
  
  getFromLocalStorage(key) {
    try {
      const data = localStorage.getItem(key)
      return data ? JSON.parse(data) : null
    } catch (e) {
      console.error('LocalStorage error:', e)
      return null
    }
  }
  
  // Calculate stats locally
  calculateLocalStats(messages) {
    const userMessages = messages.filter(m => m.message_type === 'user').length
    const adminMessages = messages.filter(m => m.message_type === 'admin').length
    const botMessages = messages.filter(m => m.message_type === 'bot').length
    
    return {
      total_messages: messages.length,
      user_messages: userMessages,
      admin_messages: adminMessages,
      bot_messages: botMessages,
      first_message: messages[0]?.timestamp,
      last_message: messages[messages.length - 1]?.timestamp
    }
  }
}

// Export
window.CRUDManager = CRUDManager
