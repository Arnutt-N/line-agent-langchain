// ===== Message Management UI =====
// Enhanced message operations with UI components

class MessageManager {
  constructor(crudManager) {
    this.crud = crudManager
    this.selectedMessages = new Set()
    this.searchTerm = ''
    this.currentPage = 1
    this.pageSize = 50
    this.isLoading = false
  }

  // Initialize message management UI
  initializeUI() {
    this.createMessageToolbar()
    this.createSearchUI()
    this.createBulkActions()
    this.attachEventListeners()
  }

  // Create message toolbar
  createMessageToolbar() {
    const toolbar = document.createElement('div')
    toolbar.id = 'message-toolbar'
    toolbar.className = 'message-toolbar hidden'
    toolbar.innerHTML = `
      <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-t-lg">
        <div class="flex items-center gap-2">
          <button id="select-all-messages" class="btn-icon" title="Select All">
            <i data-lucide="check-square" class="w-4 h-4"></i>
          </button>
          <button id="refresh-messages" class="btn-icon" title="Refresh">
            <i data-lucide="refresh-cw" class="w-4 h-4"></i>
          </button>
          <span class="text-sm text-gray-600">
            <span id="selected-count">0</span> selected
          </span>
        </div>
        
        <div class="flex items-center gap-2">
          <button id="mark-read" class="btn-secondary" disabled>
            <i data-lucide="check" class="w-4 h-4 mr-1"></i>
            Mark Read
          </button>
          <button id="export-messages" class="btn-secondary">
            <i data-lucide="download" class="w-4 h-4 mr-1"></i>
            Export
          </button>
          <button id="delete-messages" class="btn-danger" disabled>
            <i data-lucide="trash-2" class="w-4 h-4 mr-1"></i>
            Delete
          </button>
        </div>
      </div>
    `
    
    const chatWindow = document.getElementById('chat-window')
    const messagesDiv = document.getElementById('chat-messages')
    if (chatWindow && messagesDiv) {
      chatWindow.insertBefore(toolbar, messagesDiv)
    }
  }

  // Create search UI
  createSearchUI() {
    const searchContainer = document.createElement('div')
    searchContainer.id = 'message-search-container'
    searchContainer.className = 'message-search-container hidden'
    searchContainer.innerHTML = `
      <div class="p-3 bg-gray-50 dark:bg-gray-800 border-b">
        <div class="flex items-center gap-2">
          <div class="flex-1 relative">
            <i data-lucide="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"></i>
            <input type="text" 
                   id="message-search" 
                   class="w-full pl-10 pr-4 py-2 border rounded-lg"
                   placeholder="Search messages...">
          </div>
          <input type="date" id="date-from" class="px-3 py-2 border rounded-lg" title="From date">
          <input type="date" id="date-to" class="px-3 py-2 border rounded-lg" title="To date">
          <button id="search-messages-btn" class="btn-primary">
            Search
          </button>
          <button id="clear-search" class="btn-secondary">
            Clear
          </button>
        </div>
        
        <div id="search-results-info" class="mt-2 text-sm text-gray-600 hidden">
          Found <span id="results-count">0</span> messages
        </div>
      </div>
    `
    
    const toolbar = document.getElementById('message-toolbar')
    if (toolbar) {
      toolbar.parentNode.insertBefore(searchContainer, toolbar.nextSibling)
    }
  }

  // Create bulk actions menu
  createBulkActions() {
    const bulkMenu = document.createElement('div')
    bulkMenu.id = 'bulk-actions-menu'
    bulkMenu.className = 'bulk-actions-menu hidden'
    bulkMenu.innerHTML = `
      <div class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-50">
        <button class="bulk-action-item" data-action="mark-read">
          <i data-lucide="check" class="w-4 h-4 mr-2"></i>
          Mark as Read
        </button>
        <button class="bulk-action-item" data-action="mark-unread">
          <i data-lucide="circle" class="w-4 h-4 mr-2"></i>
          Mark as Unread
        </button>
        <hr class="my-1">
        <button class="bulk-action-item" data-action="export-selected">
          <i data-lucide="download" class="w-4 h-4 mr-2"></i>
          Export Selected
        </button>
        <button class="bulk-action-item text-red-600" data-action="delete-selected">
          <i data-lucide="trash-2" class="w-4 h-4 mr-2"></i>
          Delete Selected
        </button>
      </div>
    `
    
    document.body.appendChild(bulkMenu)
  }

  // Attach event listeners
  attachEventListeners() {
    // Toolbar buttons
    document.getElementById('select-all-messages')?.addEventListener('click', () => this.toggleSelectAll())
    document.getElementById('refresh-messages')?.addEventListener('click', () => this.refreshMessages())
    document.getElementById('mark-read')?.addEventListener('click', () => this.markSelectedAsRead())
    document.getElementById('export-messages')?.addEventListener('click', () => this.exportMessages())
    document.getElementById('delete-messages')?.addEventListener('click', () => this.deleteSelected())
    
    // Search
    document.getElementById('search-messages-btn')?.addEventListener('click', () => this.searchMessages())
    document.getElementById('clear-search')?.addEventListener('click', () => this.clearSearch())
    document.getElementById('message-search')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.searchMessages()
    })
    
    // Bulk actions
    document.querySelectorAll('.bulk-action-item').forEach(item => {
      item.addEventListener('click', (e) => this.handleBulkAction(e.currentTarget.dataset.action))
    })
  }

  // Show toolbar when in chat
  showToolbar() {
    document.getElementById('message-toolbar')?.classList.remove('hidden')
    document.getElementById('message-search-container')?.classList.remove('hidden')
  }

  // Hide toolbar
  hideToolbar() {
    document.getElementById('message-toolbar')?.classList.add('hidden')
    document.getElementById('message-search-container')?.classList.add('hidden')
  }

  // Load messages with enhancements
  async loadMessages(userId, options = {}) {
    if (this.isLoading) return
    
    this.isLoading = true
    this.showLoadingState()
    
    try {
      const result = await this.crud.readMessages(userId, {
        limit: this.pageSize,
        offset: (this.currentPage - 1) * this.pageSize,
        search: this.searchTerm,
        ...options
      })
      
      if (result.success) {
        this.displayMessages(result.data)
        this.updatePagination(result.total)
        
        if (result.fromCache) {
          this.showCacheIndicator()
        }
      } else {
        this.showError(result.error)
      }
    } finally {
      this.isLoading = false
      this.hideLoadingState()
    }
  }

  // Display messages with selection
  displayMessages(messages) {
    const messagesDiv = document.getElementById('chat-messages')
    if (!messagesDiv) return
    
    messagesDiv.innerHTML = ''
    this.selectedMessages.clear()
    
    messages.forEach(msg => {
      const messageEl = this.createMessageElement(msg)
      messagesDiv.appendChild(messageEl)
    })
    
    this.updateSelectionCount()
    lucide.createIcons()
  }

  // Create enhanced message element
  createMessageElement(message) {
    const div = document.createElement('div')
    div.className = `message-wrapper ${message.message_type} ${message.is_read === false ? 'unread' : ''}`
    div.dataset.messageId = message.id
    
    const isUser = message.message_type === 'user'
    const showCheckbox = !isUser || this.isAdminMode()
    
    div.innerHTML = `
      <div class="flex items-start gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
        ${showCheckbox ? `
          <input type="checkbox" 
                 class="message-checkbox mt-1" 
                 data-message-id="${message.id}"
                 onchange="messageManager.toggleSelection('${message.id}')">
        ` : ''}
        
        <div class="flex-1">
          <div class="message ${message.message_type}">
            <div class="message-header flex items-center justify-between mb-1">
              <span class="text-xs font-medium">${this.getSenderName(message)}</span>
              <span class="text-xs text-gray-500">${this.formatTime(message.timestamp)}</span>
            </div>
            <div class="message-content">${message.message_content || message.text}</div>
            ${message.edited ? '<span class="text-xs text-gray-400">(edited)</span>' : ''}
          </div>
          
          <div class="message-actions opacity-0 hover:opacity-100 transition-opacity">
            <button class="btn-icon-sm" onclick="messageManager.editMessage('${message.id}')" title="Edit">
              <i data-lucide="edit-2" class="w-3 h-3"></i>
            </button>
            <button class="btn-icon-sm" onclick="messageManager.replyToMessage('${message.id}')" title="Reply">
              <i data-lucide="reply" class="w-3 h-3"></i>
            </button>
            <button class="btn-icon-sm" onclick="messageManager.deleteMessage('${message.id}')" title="Delete">
              <i data-lucide="trash-2" class="w-3 h-3"></i>
            </button>
          </div>
        </div>
      </div>
    `
    
    return div
  }

  // Toggle message selection
  toggleSelection(messageId) {
    if (this.selectedMessages.has(messageId)) {
      this.selectedMessages.delete(messageId)
    } else {
      this.selectedMessages.add(messageId)
    }
    this.updateSelectionCount()
    this.updateBulkActionButtons()
  }

  // Select/deselect all
  toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.message-checkbox')
    const allSelected = this.selectedMessages.size === checkboxes.length
    
    checkboxes.forEach(cb => {
      cb.checked = !allSelected
      if (!allSelected) {
        this.selectedMessages.add(cb.dataset.messageId)
      } else {
        this.selectedMessages.delete(cb.dataset.messageId)
      }
    })
    
    this.updateSelectionCount()
    this.updateBulkActionButtons()
  }

  // Search messages
  async searchMessages() {
    this.searchTerm = document.getElementById('message-search').value
    const dateFrom = document.getElementById('date-from').value
    const dateTo = document.getElementById('date-to').value
    
    await this.loadMessages(selectedUser, { dateFrom, dateTo })
    
    document.getElementById('search-results-info').classList.remove('hidden')
  }

  // Export messages
  async exportMessages() {
    const format = await this.showExportDialog()
    if (!format) return
    
    try {
      const messages = this.selectedMessages.size > 0 
        ? await this.getSelectedMessages()
        : await this.getAllMessages()
      
      if (format === 'csv') {
        this.exportAsCSV(messages)
      } else if (format === 'json') {
        this.exportAsJSON(messages)
      }
      
      this.showNotification('Messages exported successfully!', 'success')
    } catch (error) {
      this.showNotification('Export failed: ' + error.message, 'error')
    }
  }

  // Continue in next part...
}

// Export
window.MessageManager = MessageManager

  // ===== Export Functions =====
  
  exportAsCSV(messages) {
    const headers = ['ID', 'Sender', 'Type', 'Message', 'Timestamp']
    const rows = messages.map(msg => [
      msg.id,
      this.getSenderName(msg),
      msg.message_type,
      `"${msg.message_content || msg.text}"`,
      new Date(msg.timestamp).toLocaleString('th-TH')
    ])
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    this.downloadFile(csv, 'messages.csv', 'text/csv')
  }
  
  exportAsJSON(messages) {
    const json = JSON.stringify(messages, null, 2)
    this.downloadFile(json, 'messages.json', 'application/json')
  }
  
  downloadFile(content, filename, type) {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  // ===== Utility Functions =====
  
  getSenderName(message) {
    switch (message.message_type) {
      case 'user': return message.display_name || 'User'
      case 'admin': return 'Admin'
      case 'bot': return 'Bot'
      case 'system': return 'System'
      default: return 'Unknown'
    }
  }
  
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    
    return date.toLocaleString('th-TH', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  isAdminMode() {
    return true // Can be configured based on user role
  }
  
  updateSelectionCount() {
    const count = this.selectedMessages.size
    document.getElementById('selected-count').textContent = count
  }
  
  updateBulkActionButtons() {
    const hasSelection = this.selectedMessages.size > 0
    document.getElementById('mark-read').disabled = !hasSelection
    document.getElementById('delete-messages').disabled = !hasSelection
  }
  
  showLoadingState() {
    const messagesDiv = document.getElementById('chat-messages')
    if (messagesDiv) {
      messagesDiv.innerHTML = `
        <div class="flex items-center justify-center h-full">
          <div class="text-center">
            <div class="spinner mb-4"></div>
            <p class="text-gray-500">Loading messages...</p>
          </div>
        </div>
      `
    }
  }
  
  hideLoadingState() {
    // Loading state is replaced by actual content
  }
  
  showError(error) {
    const messagesDiv = document.getElementById('chat-messages')
    if (messagesDiv) {
      messagesDiv.innerHTML = `
        <div class="flex items-center justify-center h-full">
          <div class="text-center text-red-500">
            <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-4"></i>
            <p>Error loading messages</p>
            <p class="text-sm">${error}</p>
            <button onclick="messageManager.refreshMessages()" class="btn-primary mt-4">
              Retry
            </button>
          </div>
        </div>
      `
      lucide.createIcons()
    }
  }
  
  showNotification(message, type = 'info') {
    const notification = document.createElement('div')
    notification.className = `notification notification-${type} animate-slideIn`
    notification.innerHTML = `
      <div class="flex items-center">
        <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}" class="w-5 h-5 mr-2"></i>
        <span>${message}</span>
      </div>
    `
    
    document.body.appendChild(notification)
    lucide.createIcons()
    
    setTimeout(() => {
      notification.classList.add('animate-fadeOut')
      setTimeout(() => notification.remove(), 300)
    }, 3000)
  }
  
  async showExportDialog() {
    return new Promise(resolve => {
      const dialog = document.createElement('div')
      dialog.className = 'dialog-overlay'
      dialog.innerHTML = `
        <div class="dialog-content">
          <h3 class="text-lg font-semibold mb-4">Export Messages</h3>
          <p class="mb-4">Choose export format:</p>
          <div class="flex gap-2">
            <button onclick="resolve('csv')" class="btn-primary">CSV</button>
            <button onclick="resolve('json')" class="btn-primary">JSON</button>
            <button onclick="resolve(null)" class="btn-secondary">Cancel</button>
          </div>
        </div>
      `
      
      dialog.onclick = (e) => {
        if (e.target === dialog) resolve(null)
      }
      
      window.resolve = resolve
      document.body.appendChild(dialog)
      
      // Cleanup
      dialog.addEventListener('click', () => {
        delete window.resolve
        dialog.remove()
      })
    })
  }
  
  // ===== Additional CRUD Operations =====
  
  async editMessage(messageId) {
    const message = await this.getMessageById(messageId)
    if (!message) return
    
    const newContent = prompt('Edit message:', message.message_content)
    if (!newContent || newContent === message.message_content) return
    
    const result = await this.crud.updateMessage(messageId, {
      message_content: newContent,
      edited: true,
      edited_at: new Date().toISOString()
    })
    
    if (result.success) {
      this.refreshMessages()
      this.showNotification('Message updated', 'success')
    } else {
      this.showNotification('Failed to update message', 'error')
    }
  }
  
  async replyToMessage(messageId) {
    const message = await this.getMessageById(messageId)
    if (!message) return
    
    const input = document.getElementById('chat-input')
    if (input) {
      input.value = `@reply ${messageId} `
      input.focus()
    }
  }
  
  async deleteMessage(messageId) {
    if (!confirm('Delete this message?')) return
    
    const result = await this.crud.deleteMessage(messageId)
    
    if (result.success) {
      document.querySelector(`[data-message-id="${messageId}"]`)?.remove()
      this.showNotification('Message deleted', 'success')
    } else {
      this.showNotification('Failed to delete message', 'error')
    }
  }
  
  async getMessageById(messageId) {
    // Implementation depends on your data structure
    const messagesDiv = document.getElementById('chat-messages')
    const messageEl = messagesDiv.querySelector(`[data-message-id="${messageId}"]`)
    // Return message data
  }
  
  async markSelectedAsRead() {
    const messageIds = Array.from(this.selectedMessages)
    
    const result = await this.crud.bulkUpdateMessages(selectedUser, {
      message_ids: messageIds,
      updates: { is_read: true }
    })
    
    if (result.success) {
      this.selectedMessages.clear()
      this.refreshMessages()
      this.showNotification(`${messageIds.length} messages marked as read`, 'success')
    }
  }
  
  async deleteSelected() {
    if (!confirm(`Delete ${this.selectedMessages.size} messages?`)) return
    
    const messageIds = Array.from(this.selectedMessages)
    let successCount = 0
    
    for (const id of messageIds) {
      const result = await this.crud.deleteMessage(id)
      if (result.success) successCount++
    }
    
    this.selectedMessages.clear()
    this.refreshMessages()
    this.showNotification(`${successCount} messages deleted`, 'success')
  }
  
  async refreshMessages() {
    if (selectedUser) {
      await this.loadMessages(selectedUser)
    }
  }
  
  clearSearch() {
    document.getElementById('message-search').value = ''
    document.getElementById('date-from').value = ''
    document.getElementById('date-to').value = ''
    this.searchTerm = ''
    this.refreshMessages()
    document.getElementById('search-results-info').classList.add('hidden')
  }
  
  async handleBulkAction(action) {
    switch (action) {
      case 'mark-read':
        await this.markSelectedAsRead()
        break
      case 'mark-unread':
        await this.markSelectedAsUnread()
        break
      case 'export-selected':
        await this.exportSelected()
        break
      case 'delete-selected':
        await this.deleteSelected()
        break
    }
    
    document.getElementById('bulk-actions-menu').classList.add('hidden')
  }
