// ===== Chat History Management Module =====
// Advanced chat history features with search, export, and analytics

class ChatHistoryManager {
  constructor(crudManager) {
    this.crud = crudManager
    this.conversations = new Map()
    this.searchIndex = new Map()
    this.currentConversation = null
    this.filters = {
      dateRange: 30,
      searchTerm: '',
      messageType: 'all',
      userFilter: null,
      sortBy: 'recent'
    }
  }

  // Initialize chat history UI
  initializeUI() {
    this.createHistoryLayout()
    this.setupEventListeners()
    this.initializeSearch()
  }

  // Create history management layout
  createHistoryLayout() {
    const container = document.createElement('div')
    container.id = 'history-management'
    container.className = 'history-management-container hidden'
    container.innerHTML = `
      <div class="history-header">
        <h2 class="text-xl font-bold">Chat History Management</h2>
        <div class="history-actions">
          <button id="history-back" class="btn-secondary">
            <i data-lucide="arrow-left" class="w-4 h-4 mr-2"></i>
            Back
          </button>
        </div>
      </div>

      <div class="history-controls">
        <!-- Search and Filters -->
        <div class="history-search-bar">
          <div class="search-input-group">
            <i data-lucide="search" class="search-icon"></i>
            <input type="text" 
                   id="history-search" 
                   class="history-search-input" 
                   placeholder="Search conversations...">
            <button id="advanced-search-toggle" class="btn-icon" title="Advanced Search">
              <i data-lucide="filter" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <!-- Advanced Search Panel -->
        <div id="advanced-search-panel" class="advanced-search-panel hidden">
          <div class="search-filters">
            <div class="filter-group">
              <label>Date Range</label>
              <select id="history-date-range" class="filter-select">
                <option value="7">Last 7 days</option>
                <option value="30" selected>Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
                <option value="all">All time</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Message Type</label>
              <select id="history-message-type" class="filter-select">
                <option value="all">All Types</option>
                <option value="user">User Messages</option>
                <option value="bot">Bot Messages</option>
                <option value="admin">Admin Messages</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Sort By</label>
              <select id="history-sort" class="filter-select">
                <option value="recent">Most Recent</option>
                <option value="oldest">Oldest First</option>
                <option value="messages">Most Messages</option>
                <option value="duration">Longest Duration</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>Keywords</label>
              <input type="text" 
                     id="history-keywords" 
                     class="filter-input" 
                     placeholder="Comma separated...">
            </div>
          </div>
          
          <div class="search-actions">
            <button id="apply-filters" class="btn-primary">Apply Filters</button>
            <button id="clear-filters" class="btn-secondary">Clear All</button>
          </div>
        </div>

        <!-- Stats Bar -->
        <div class="history-stats-bar">
          <div class="stat-item">
            <span class="stat-label">Total Conversations:</span>
            <span class="stat-value" id="total-conversations">0</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Messages:</span>
            <span class="stat-value" id="total-messages">0</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Date Range:</span>
            <span class="stat-value" id="date-range-display">Last 30 days</span>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="history-content">
        <!-- Conversations List -->
        <div class="conversations-panel">
          <div class="panel-header">
            <h3 class="panel-title">Conversations</h3>
            <div class="panel-actions">
              <button id="export-conversations" class="btn-icon" title="Export All">
                <i data-lucide="download" class="w-4 h-4"></i>
              </button>
              <button id="refresh-conversations" class="btn-icon" title="Refresh">
                <i data-lucide="refresh-cw" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
          
          <div id="conversations-list" class="conversations-list">
            <div class="loading-placeholder">Loading conversations...</div>
          </div>
          
          <div class="panel-footer">
            <button id="load-more-conversations" class="btn-secondary w-full hidden">
              Load More
            </button>
          </div>
        </div>

        <!-- Conversation Detail -->
        <div class="conversation-detail-panel">
          <div id="conversation-placeholder" class="conversation-placeholder">
            <i data-lucide="message-square" class="w-16 h-16 text-gray-300"></i>
            <p class="text-gray-500">Select a conversation to view details</p>
          </div>
          
          <div id="conversation-detail" class="conversation-detail hidden">
            <!-- Header -->
            <div class="detail-header">
              <div class="user-info">
                <img id="detail-user-avatar" src="" class="user-avatar" alt="">
                <div>
                  <h3 id="detail-user-name" class="user-name"></h3>
                  <p id="detail-session-info" class="session-info"></p>
                </div>
              </div>
              
              <div class="detail-actions">
                <button id="print-conversation" class="btn-icon" title="Print">
                  <i data-lucide="printer" class="w-4 h-4"></i>
                </button>
                <button id="export-conversation" class="btn-icon" title="Export">
                  <i data-lucide="download" class="w-4 h-4"></i>
                </button>
                <button id="analyze-conversation" class="btn-icon" title="Analyze">
                  <i data-lucide="bar-chart-2" class="w-4 h-4"></i>
                </button>
              </div>
            </div>
            
            <!-- Messages -->
            <div id="detail-messages" class="detail-messages">
              <!-- Messages will be loaded here -->
            </div>
            
            <!-- Analytics -->
            <div id="conversation-analytics" class="conversation-analytics hidden">
              <h4 class="analytics-title">Conversation Analytics</h4>
              <div class="analytics-content">
                <!-- Analytics will be loaded here -->
              </div>
            </div>
          </div>
        </div>
      </div>
    `

    // Add to main content area
    const mainContent = document.querySelector('main')
    if (mainContent) {
      mainContent.appendChild(container)
    }

    lucide.createIcons()
  }

  // Setup event listeners
  setupEventListeners() {
    // Search
    document.getElementById('history-search')?.addEventListener('input', 
      this.debounce(() => this.performSearch(), 300))
    
    // Advanced search toggle
    document.getElementById('advanced-search-toggle')?.addEventListener('click', 
      () => this.toggleAdvancedSearch())
    
    // Filters
    document.getElementById('apply-filters')?.addEventListener('click', 
      () => this.applyFilters())
    document.getElementById('clear-filters')?.addEventListener('click', 
      () => this.clearFilters())
    
    // Actions
    document.getElementById('export-conversations')?.addEventListener('click', 
      () => this.exportAllConversations())
    document.getElementById('refresh-conversations')?.addEventListener('click', 
      () => this.loadConversations())
    document.getElementById('load-more-conversations')?.addEventListener('click', 
      () => this.loadMoreConversations())
    
    // Detail actions
    document.getElementById('print-conversation')?.addEventListener('click', 
      () => this.printConversation())
    document.getElementById('export-conversation')?.addEventListener('click', 
      () => this.exportConversation())
    document.getElementById('analyze-conversation')?.addEventListener('click', 
      () => this.analyzeConversation())
    
    // Back button
    document.getElementById('history-back')?.addEventListener('click', 
      () => this.hide())
  }

  // Show history management
  show() {
    // Hide other views
    document.getElementById('dashboard')?.classList.add('hidden')
    document.getElementById('chat-window')?.classList.add('hidden')
    document.getElementById('analytics-view')?.classList.add('hidden')
    
    // Show history management
    document.getElementById('history-management')?.classList.remove('hidden')
    
    // Load initial data
    this.loadConversations()
  }

  // Hide history management
  hide() {
    document.getElementById('history-management')?.classList.add('hidden')
    document.getElementById('dashboard')?.classList.remove('hidden')
  }

  // Load conversations
  async loadConversations() {
    this.showLoadingState()
    
    try {
      // Get unique conversations
      const conversations = await this.fetchConversations()
      
      // Process and display
      this.processConversations(conversations)
      this.displayConversations()
      this.updateStats()
      
    } catch (error) {
      console.error('Error loading conversations:', error)
      this.showError('Failed to load conversations')
    } finally {
      this.hideLoadingState()
    }
  }

  // Fetch conversations from API
  async fetchConversations() {
    // This would normally fetch from API
    // For now, generate mock data
    const conversations = []
    const users = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown']
    
    for (let i = 0; i < 20; i++) {
      const userId = `U${Math.random().toString(36).substr(2, 9)}`
      const userName = users[Math.floor(Math.random() * users.length)]
      const messageCount = Math.floor(Math.random() * 50) + 5
      const startDate = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
      const endDate = new Date(startDate.getTime() + Math.random() * 2 * 60 * 60 * 1000)
      
      conversations.push({
        id: `conv_${i}`,
        userId: userId,
        userName: userName,
        avatar: `https://i.pravatar.cc/150?u=${userId}`,
        messageCount: messageCount,
        startTime: startDate.toISOString(),
        endTime: endDate.toISOString(),
        lastMessage: this.generateMockMessage(),
        status: Math.random() > 0.3 ? 'resolved' : 'active'
      })
    }
    
    return conversations
  }

  // Process conversations
  processConversations(conversations) {
    this.conversations.clear()
    
    conversations.forEach(conv => {
      this.conversations.set(conv.id, conv)
      
      // Build search index
      this.indexConversation(conv)
    })
  }

  // Continue in next part...
}

// Export
window.ChatHistoryManager = ChatHistoryManager

  // ===== Display Functions =====
  
  displayConversations() {
    const listEl = document.getElementById('conversations-list')
    if (!listEl) return
    
    const filtered = this.getFilteredConversations()
    
    if (filtered.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state">
          <i data-lucide="inbox" class="w-12 h-12 text-gray-300"></i>
          <p class="text-gray-500">No conversations found</p>
        </div>
      `
      lucide.createIcons()
      return
    }
    
    listEl.innerHTML = filtered.map(conv => this.createConversationCard(conv)).join('')
    
    // Add click handlers
    listEl.querySelectorAll('.conversation-card').forEach(card => {
      card.addEventListener('click', () => {
        const convId = card.dataset.conversationId
        this.selectConversation(convId)
      })
    })
    
    lucide.createIcons()
  }

  createConversationCard(conv) {
    const duration = this.calculateDuration(conv.startTime, conv.endTime)
    const timeAgo = this.formatTimeAgo(conv.endTime)
    const statusClass = conv.status === 'resolved' ? 'status-resolved' : 'status-active'
    
    return `
      <div class="conversation-card" data-conversation-id="${conv.id}">
        <div class="conversation-header">
          <img src="${conv.avatar}" alt="${conv.userName}" class="user-avatar">
          <div class="conversation-info">
            <h4 class="conversation-title">${conv.userName}</h4>
            <p class="conversation-meta">
              <span>${conv.messageCount} messages</span> • 
              <span>${duration}</span> • 
              <span>${timeAgo}</span>
            </p>
          </div>
          <span class="conversation-status ${statusClass}">
            ${conv.status}
          </span>
        </div>
        <div class="conversation-preview">
          ${conv.lastMessage}
        </div>
      </div>
    `
  }

  // Select and display conversation details
  async selectConversation(conversationId) {
    this.currentConversation = this.conversations.get(conversationId)
    if (!this.currentConversation) return
    
    // Update UI
    document.querySelectorAll('.conversation-card').forEach(card => {
      card.classList.toggle('selected', card.dataset.conversationId === conversationId)
    })
    
    // Show detail panel
    document.getElementById('conversation-placeholder')?.classList.add('hidden')
    document.getElementById('conversation-detail')?.classList.remove('hidden')
    
    // Update header
    this.updateDetailHeader()
    
    // Load messages
    await this.loadConversationMessages()
  }

  updateDetailHeader() {
    const conv = this.currentConversation
    
    document.getElementById('detail-user-avatar').src = conv.avatar
    document.getElementById('detail-user-name').textContent = conv.userName
    document.getElementById('detail-session-info').textContent = 
      `${conv.messageCount} messages • ${this.formatDateRange(conv.startTime, conv.endTime)}`
  }

  async loadConversationMessages() {
    const messagesEl = document.getElementById('detail-messages')
    if (!messagesEl) return
    
    messagesEl.innerHTML = '<div class="loading">Loading messages...</div>'
    
    try {
      // Fetch messages (mock for now)
      const messages = await this.fetchConversationMessages(this.currentConversation.id)
      
      // Display messages
      messagesEl.innerHTML = messages.map(msg => this.createMessageElement(msg)).join('')
      
      // Scroll to bottom
      messagesEl.scrollTop = messagesEl.scrollHeight
      
    } catch (error) {
      messagesEl.innerHTML = '<div class="error">Failed to load messages</div>'
    }
  }

  createMessageElement(msg) {
    const time = new Date(msg.timestamp).toLocaleTimeString('th-TH', {
      hour: '2-digit',
      minute: '2-digit'
    })
    
    return `
      <div class="history-message ${msg.type}">
        <div class="message-header">
          <span class="message-sender">${msg.sender}</span>
          <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${msg.content}</div>
      </div>
    `
  }

  // ===== Search & Filter Functions =====
  
  initializeSearch() {
    // Build search index for existing conversations
    this.conversations.forEach(conv => {
      this.indexConversation(conv)
    })
  }

  indexConversation(conv) {
    const searchText = `${conv.userName} ${conv.lastMessage}`.toLowerCase()
    const words = searchText.split(/\s+/)
    
    words.forEach(word => {
      if (word.length < 2) return
      
      if (!this.searchIndex.has(word)) {
        this.searchIndex.set(word, new Set())
      }
      this.searchIndex.get(word).add(conv.id)
    })
  }

  performSearch() {
    const searchTerm = document.getElementById('history-search').value.toLowerCase()
    this.filters.searchTerm = searchTerm
    this.displayConversations()
  }

  getFilteredConversations() {
    let filtered = Array.from(this.conversations.values())
    
    // Search filter
    if (this.filters.searchTerm) {
      const searchWords = this.filters.searchTerm.split(/\s+/)
      const matchingIds = new Set()
      
      searchWords.forEach(word => {
        if (this.searchIndex.has(word)) {
          this.searchIndex.get(word).forEach(id => matchingIds.add(id))
        }
      })
      
      filtered = filtered.filter(conv => matchingIds.has(conv.id))
    }
    
    // Date range filter
    if (this.filters.dateRange !== 'all') {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - parseInt(this.filters.dateRange))
      
      filtered = filtered.filter(conv => 
        new Date(conv.endTime) >= cutoffDate
      )
    }
    
    // Message type filter
    if (this.filters.messageType !== 'all') {
      // This would filter based on message types in the conversation
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (this.filters.sortBy) {
        case 'oldest':
          return new Date(a.startTime) - new Date(b.startTime)
        case 'messages':
          return b.messageCount - a.messageCount
        case 'duration':
          const durA = new Date(a.endTime) - new Date(a.startTime)
          const durB = new Date(b.endTime) - new Date(b.startTime)
          return durB - durA
        default: // recent
          return new Date(b.endTime) - new Date(a.endTime)
      }
    })
    
    return filtered
  }

  toggleAdvancedSearch() {
    const panel = document.getElementById('advanced-search-panel')
    panel?.classList.toggle('hidden')
  }

  applyFilters() {
    // Get filter values
    this.filters.dateRange = document.getElementById('history-date-range').value
    this.filters.messageType = document.getElementById('history-message-type').value
    this.filters.sortBy = document.getElementById('history-sort').value
    
    const keywords = document.getElementById('history-keywords').value
    if (keywords) {
      this.filters.searchTerm = keywords.toLowerCase()
      document.getElementById('history-search').value = keywords
    }
    
    // Update display
    this.displayConversations()
    this.updateStats()
    
    // Close panel
    this.toggleAdvancedSearch()
  }

  clearFilters() {
    // Reset filters
    this.filters = {
      dateRange: 30,
      searchTerm: '',
      messageType: 'all',
      userFilter: null,
      sortBy: 'recent'
    }
    
    // Reset UI
    document.getElementById('history-search').value = ''
    document.getElementById('history-date-range').value = '30'
    document.getElementById('history-message-type').value = 'all'
    document.getElementById('history-sort').value = 'recent'
    document.getElementById('history-keywords').value = ''
    
    // Update display
    this.displayConversations()
    this.updateStats()
  }

  // ===== Analytics Functions =====
  
  async analyzeConversation() {
    if (!this.currentConversation) return
    
    const analyticsEl = document.getElementById('conversation-analytics')
    const messagesEl = document.getElementById('detail-messages')
    
    // Toggle analytics view
    analyticsEl?.classList.toggle('hidden')
    
    if (!analyticsEl?.classList.contains('hidden')) {
      // Generate analytics
      const analytics = await this.generateConversationAnalytics()
      
      analyticsEl.querySelector('.analytics-content').innerHTML = `
        <div class="analytics-grid">
          <div class="analytics-card">
            <h5>Message Distribution</h5>
            <canvas id="message-dist-chart" width="200" height="150"></canvas>
          </div>
          
          <div class="analytics-card">
            <h5>Response Times</h5>
            <div class="metric">
              <span class="metric-label">Average:</span>
              <span class="metric-value">${analytics.avgResponseTime}s</span>
            </div>
            <div class="metric">
              <span class="metric-label">Fastest:</span>
              <span class="metric-value">${analytics.minResponseTime}s</span>
            </div>
          </div>
          
          <div class="analytics-card">
            <h5>Conversation Flow</h5>
            <div class="flow-diagram">
              ${this.createFlowDiagram(analytics.flow)}
            </div>
          </div>
          
          <div class="analytics-card">
            <h5>Key Topics</h5>
            <div class="topics-cloud">
              ${analytics.topics.map(topic => 
                `<span class="topic-tag">${topic}</span>`
              ).join('')}
            </div>
          </div>
        </div>
      `
      
      // Render charts
      this.renderMessageDistChart(analytics.messageTypes)
    }
  }

  async generateConversationAnalytics() {
    // Mock analytics data
    return {
      messageTypes: {
        user: 15,
        bot: 12,
        admin: 3
      },
      avgResponseTime: 45,
      minResponseTime: 5,
      maxResponseTime: 120,
      flow: ['greeting', 'question', 'answer', 'followup', 'resolution'],
      topics: ['account', 'billing', 'support', 'technical']
    }
  }

  renderMessageDistChart(data) {
    const canvas = document.getElementById('message-dist-chart')
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['User', 'Bot', 'Admin'],
        datasets: [{
          data: [data.user, data.bot, data.admin],
          backgroundColor: ['#3b82f6', '#10b981', '#f59e0b']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  }

  // ===== Export Functions =====
  
  async exportConversation() {
    if (!this.currentConversation) return
    
    const format = await this.showExportDialog()
    if (!format) return
    
    try {
      const messages = await this.fetchConversationMessages(this.currentConversation.id)
      
      if (format === 'pdf') {
        this.exportAsPDF(this.currentConversation, messages)
      } else if (format === 'txt') {
        this.exportAsText(this.currentConversation, messages)
      } else if (format === 'json') {
        this.exportAsJSON(this.currentConversation, messages)
      }
      
      this.showNotification('Conversation exported successfully!', 'success')
    } catch (error) {
      this.showNotification('Export failed: ' + error.message, 'error')
    }
  }

  async exportAllConversations() {
    const filtered = this.getFilteredConversations()
    
    if (filtered.length === 0) {
      this.showNotification('No conversations to export', 'info')
      return
    }
    
    const format = await this.showExportDialog()
    if (!format) return
    
    // For simplicity, export as JSON
    const data = {
      exportDate: new Date().toISOString(),
      totalConversations: filtered.length,
      conversations: filtered
    }
    
    this.downloadFile(JSON.stringify(data, null, 2), 'conversations.json', 'application/json')
    this.showNotification(`Exported ${filtered.length} conversations`, 'success')
  }

  // Continue with utility functions...

  // ===== Utility Functions =====
  
  calculateDuration(startTime, endTime) {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const diff = end - start
    
    const hours = Math.floor(diff / 3600000)
    const minutes = Math.floor((diff % 3600000) / 60000)
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  formatTimeAgo(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 86400000) return 'Today'
    if (diff < 172800000) return 'Yesterday'
    if (diff < 604800000) return `${Math.floor(diff / 86400000)} days ago`
    if (diff < 2592000000) return `${Math.floor(diff / 604800000)} weeks ago`
    
    return date.toLocaleDateString('th-TH', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  formatDateRange(startTime, endTime) {
    const start = new Date(startTime)
    const end = new Date(endTime)
    
    const dateOptions = { month: 'short', day: 'numeric' }
    const timeOptions = { hour: '2-digit', minute: '2-digit' }
    
    const startDate = start.toLocaleDateString('th-TH', dateOptions)
    const startTimeStr = start.toLocaleTimeString('th-TH', timeOptions)
    const endTimeStr = end.toLocaleTimeString('th-TH', timeOptions)
    
    return `${startDate} ${startTimeStr} - ${endTimeStr}`
  }

  updateStats() {
    const filtered = this.getFilteredConversations()
    const totalMessages = filtered.reduce((sum, conv) => sum + conv.messageCount, 0)
    
    document.getElementById('total-conversations').textContent = filtered.length
    document.getElementById('total-messages').textContent = totalMessages
    
    const dateRangeText = this.filters.dateRange === 'all' 
      ? 'All time' 
      : `Last ${this.filters.dateRange} days`
    document.getElementById('date-range-display').textContent = dateRangeText
  }

  showLoadingState() {
    const listEl = document.getElementById('conversations-list')
    if (listEl) {
      listEl.innerHTML = '<div class="loading-placeholder">Loading conversations...</div>'
    }
  }

  hideLoadingState() {
    // Loading is replaced by content
  }

  showError(message) {
    const listEl = document.getElementById('conversations-list')
    if (listEl) {
      listEl.innerHTML = `
        <div class="error-state">
          <i data-lucide="alert-circle" class="w-12 h-12 text-red-500"></i>
          <p class="text-red-600">${message}</p>
          <button onclick="chatHistoryManager.loadConversations()" class="btn-primary mt-4">
            Retry
          </button>
        </div>
      `
      lucide.createIcons()
    }
  }

  async showExportDialog() {
    return new Promise(resolve => {
      const dialog = document.createElement('div')
      dialog.className = 'dialog-overlay'
      dialog.innerHTML = `
        <div class="dialog-content">
          <h3 class="text-lg font-semibold mb-4">Export Conversation</h3>
          <p class="mb-4">Choose export format:</p>
          <div class="flex gap-2">
            <button onclick="resolve('pdf')" class="btn-primary">PDF</button>
            <button onclick="resolve('txt')" class="btn-primary">Text</button>
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
      
      dialog.addEventListener('click', () => {
        delete window.resolve
        dialog.remove()
      })
    })
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

  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }

  // ===== Mock Data Functions =====
  
  generateMockMessage() {
    const messages = [
      'สอบถามเกี่ยวกับการลาพักร้อน',
      'ขอข้อมูลเกี่ยวกับสวัสดิการ',
      'แจ้งปัญหาระบบ HR',
      'สอบถามขั้นตอนการขอเอกสาร',
      'ติดต่อเรื่องการอบรม'
    ]
    return messages[Math.floor(Math.random() * messages.length)]
  }

  async fetchConversationMessages(conversationId) {
    // Mock messages
    const messages = []
    const types = ['user', 'bot', 'admin']
    const senders = {
      user: this.currentConversation.userName,
      bot: 'HR Bot',
      admin: 'HR Admin'
    }
    
    for (let i = 0; i < 20; i++) {
      const type = types[Math.floor(Math.random() * types.length)]
      messages.push({
        id: `msg_${i}`,
        type: type,
        sender: senders[type],
        content: this.generateMockMessageContent(type),
        timestamp: new Date(Date.now() - (20 - i) * 5 * 60 * 1000).toISOString()
      })
    }
    
    return messages
  }

  generateMockMessageContent(type) {
    const contents = {
      user: [
        'สวัสดีครับ ขอสอบถามเกี่ยวกับการลาพักร้อนหน่อยครับ',
        'ผมมีวันลาเหลืออยู่กี่วันครับ?',
        'ขอบคุณครับ แล้วขั้นตอนการขอลาเป็นอย่างไรบ้าง?'
      ],
      bot: [
        'สวัสดีค่ะ ยินดีให้บริการค่ะ',
        'ตามข้อมูลในระบบ คุณมีวันลาพักร้อนคงเหลือ 10 วันค่ะ',
        'คุณสามารถยื่นใบลาผ่านระบบ HR Online ได้เลยค่ะ'
      ],
      admin: [
        'สวัสดีครับ ผมเป็นเจ้าหน้าที่ HR ยินดีช่วยเหลือครับ',
        'เอกสารของคุณได้รับการอนุมัติแล้วครับ',
        'มีอะไรให้ช่วยเหลือเพิ่มเติมไหมครับ?'
      ]
    }
    
    const typeContents = contents[type]
    return typeContents[Math.floor(Math.random() * typeContents.length)]
  }

  createFlowDiagram(flow) {
    return flow.map((step, index) => `
      <div class="flow-step">
        <div class="step-number">${index + 1}</div>
        <div class="step-label">${step}</div>
      </div>
      ${index < flow.length - 1 ? '<div class="flow-arrow">→</div>' : ''}
    `).join('')
  }

  exportAsText(conversation, messages) {
    let content = `Conversation with ${conversation.userName}\n`
    content += `Date: ${this.formatDateRange(conversation.startTime, conversation.endTime)}\n`
    content += `Total Messages: ${conversation.messageCount}\n`
    content += `Status: ${conversation.status}\n\n`
    content += '='.repeat(50) + '\n\n'
    
    messages.forEach(msg => {
      const time = new Date(msg.timestamp).toLocaleString('th-TH')
      content += `[${time}] ${msg.sender}: ${msg.content}\n\n`
    })
    
    this.downloadFile(content, `conversation_${conversation.id}.txt`, 'text/plain')
  }

  exportAsJSON(conversation, messages) {
    const data = {
      conversation: conversation,
      messages: messages,
      exportDate: new Date().toISOString()
    }
    
    this.downloadFile(
      JSON.stringify(data, null, 2), 
      `conversation_${conversation.id}.json`, 
      'application/json'
    )
  }

  exportAsPDF(conversation, messages) {
    // This would require a PDF library
    // For now, show a message
    this.showNotification('PDF export requires additional libraries', 'info')
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

  printConversation() {
    if (!this.currentConversation) return
    
    const printWindow = window.open('', 'PRINT', 'height=600,width=800')
    
    printWindow.document.write(`
      <html>
        <head>
          <title>Conversation - ${this.currentConversation.userName}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
            .message { margin-bottom: 15px; padding: 10px; border-radius: 5px; }
            .message.user { background-color: #e3f2fd; }
            .message.bot { background-color: #f3e5f5; }
            .message.admin { background-color: #fff3e0; }
            .sender { font-weight: bold; }
            .time { color: #666; font-size: 0.9em; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>Conversation with ${this.currentConversation.userName}</h2>
            <p>Date: ${this.formatDateRange(this.currentConversation.startTime, this.currentConversation.endTime)}</p>
            <p>Total Messages: ${this.currentConversation.messageCount}</p>
          </div>
          <div id="print-messages"></div>
        </body>
      </html>
    `)
    
    // Add messages
    const messagesEl = printWindow.document.getElementById('print-messages')
    const messages = document.getElementById('detail-messages').innerHTML
    messagesEl.innerHTML = messages
    
    printWindow.document.close()
    printWindow.focus()
    printWindow.print()
    printWindow.close()
  }

  // Load more functionality
  loadMoreConversations() {
    // Implementation for pagination
    this.showNotification('Loading more conversations...', 'info')
  }
