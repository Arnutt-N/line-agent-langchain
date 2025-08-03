// ===== Analytics Dashboard Module =====
// Real-time analytics and data visualization

class AnalyticsDashboard {
  constructor() {
    this.charts = new Map()
    this.data = {
      overview: null,
      timeline: null,
      userActivity: null,
      messageTypes: null,
      responseTime: null,
      topUsers: null
    }
    this.refreshInterval = null
    this.dateRange = 30 // days
  }

  // Initialize analytics dashboard
  async initialize() {
    this.createDashboardLayout()
    this.setupDateRangePicker()
    this.setupRefreshControls()
    await this.loadAllData()
    this.startAutoRefresh()
  }

  // Create dashboard layout
  createDashboardLayout() {
    const analyticsView = document.getElementById('analytics-view')
    if (!analyticsView) return

    analyticsView.innerHTML = `
      <div class="analytics-dashboard">
        <!-- Header Controls -->
        <div class="analytics-header mb-6">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold">Analytics Dashboard</h2>
            <div class="flex items-center gap-4">
              <div class="date-range-picker">
                <select id="date-range" class="px-3 py-2 border rounded-lg">
                  <option value="7">Last 7 days</option>
                  <option value="30" selected>Last 30 days</option>
                  <option value="90">Last 90 days</option>
                  <option value="custom">Custom range</option>
                </select>
                <div id="custom-date-range" class="hidden ml-2">
                  <input type="date" id="analytics-date-from" class="px-2 py-1 border rounded">
                  <span class="mx-2">to</span>
                  <input type="date" id="analytics-date-to" class="px-2 py-1 border rounded">
                </div>
              </div>
              <button id="refresh-analytics" class="btn-primary">
                <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                Refresh
              </button>
              <button id="export-analytics" class="btn-secondary">
                <i data-lucide="download" class="w-4 h-4 mr-2"></i>
                Export Report
              </button>
            </div>
          </div>
        </div>

        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="kpi-card">
            <div class="kpi-header">
              <i data-lucide="message-square" class="w-6 h-6 text-blue-500"></i>
              <span class="text-sm text-gray-500">Total Messages</span>
            </div>
            <div class="kpi-value" id="kpi-total-messages">
              <div class="skeleton-loader h-8 w-24"></div>
            </div>
            <div class="kpi-trend" id="kpi-messages-trend"></div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <i data-lucide="users" class="w-6 h-6 text-green-500"></i>
              <span class="text-sm text-gray-500">Active Users</span>
            </div>
            <div class="kpi-value" id="kpi-active-users">
              <div class="skeleton-loader h-8 w-24"></div>
            </div>
            <div class="kpi-trend" id="kpi-users-trend"></div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <i data-lucide="clock" class="w-6 h-6 text-purple-500"></i>
              <span class="text-sm text-gray-500">Avg Response Time</span>
            </div>
            <div class="kpi-value" id="kpi-response-time">
              <div class="skeleton-loader h-8 w-24"></div>
            </div>
            <div class="kpi-trend" id="kpi-response-trend"></div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <i data-lucide="trending-up" class="w-6 h-6 text-orange-500"></i>
              <span class="text-sm text-gray-500">Resolution Rate</span>
            </div>
            <div class="kpi-value" id="kpi-resolution-rate">
              <div class="skeleton-loader h-8 w-24"></div>
            </div>
            <div class="kpi-trend" id="kpi-resolution-trend"></div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <!-- Messages Timeline -->
          <div class="chart-container">
            <h3 class="chart-title">Messages Timeline</h3>
            <canvas id="timeline-chart"></canvas>
          </div>

          <!-- Message Types Distribution -->
          <div class="chart-container">
            <h3 class="chart-title">Message Types</h3>
            <canvas id="message-types-chart"></canvas>
          </div>

          <!-- User Activity Heatmap -->
          <div class="chart-container">
            <h3 class="chart-title">User Activity Heatmap</h3>
            <canvas id="activity-heatmap"></canvas>
          </div>

          <!-- Response Time Trend -->
          <div class="chart-container">
            <h3 class="chart-title">Response Time Trend</h3>
            <canvas id="response-time-chart"></canvas>
          </div>
        </div>

        <!-- Tables Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Top Active Users -->
          <div class="table-container">
            <h3 class="table-title">Top Active Users</h3>
            <div id="top-users-table" class="overflow-x-auto">
              <table class="analytics-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Messages</th>
                    <th>Last Active</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody id="top-users-tbody">
                  <tr><td colspan="4" class="text-center">Loading...</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recent Activity Log -->
          <div class="table-container">
            <h3 class="table-title">Recent Activity</h3>
            <div id="activity-log" class="activity-log">
              <div class="text-center text-gray-500">Loading...</div>
            </div>
          </div>
        </div>
      </div>
    `

    lucide.createIcons()
  }

  // Setup date range picker
  setupDateRangePicker() {
    const dateRangeSelect = document.getElementById('date-range')
    const customDateRange = document.getElementById('custom-date-range')

    dateRangeSelect?.addEventListener('change', (e) => {
      if (e.target.value === 'custom') {
        customDateRange.classList.remove('hidden')
      } else {
        customDateRange.classList.add('hidden')
        this.dateRange = parseInt(e.target.value)
        this.loadAllData()
      }
    })

    // Custom date range
    document.getElementById('analytics-date-from')?.addEventListener('change', () => this.handleCustomDateRange())
    document.getElementById('analytics-date-to')?.addEventListener('change', () => this.handleCustomDateRange())
  }

  // Setup refresh controls
  setupRefreshControls() {
    document.getElementById('refresh-analytics')?.addEventListener('click', () => {
      this.loadAllData()
    })

    document.getElementById('export-analytics')?.addEventListener('click', () => {
      this.exportAnalyticsReport()
    })
  }

  // Load all analytics data
  async loadAllData() {
    this.showLoadingState()

    try {
      // Load data in parallel
      const [overview, timeline, userActivity, messageTypes, responseTime, topUsers] = await Promise.all([
        this.fetchOverviewData(),
        this.fetchTimelineData(),
        this.fetchUserActivityData(),
        this.fetchMessageTypesData(),
        this.fetchResponseTimeData(),
        this.fetchTopUsersData()
      ])

      // Store data
      this.data = {
        overview,
        timeline,
        userActivity,
        messageTypes,
        responseTime,
        topUsers
      }

      // Update UI
      this.updateKPICards(overview)
      this.renderCharts()
      this.updateTables()

    } catch (error) {
      console.error('Error loading analytics data:', error)
      this.showError('Failed to load analytics data')
    } finally {
      this.hideLoadingState()
    }
  }

  // Fetch overview data
  async fetchOverviewData() {
    const response = await fetch(`/api/analytics/overview?days=${this.dateRange}`)
    if (!response.ok) throw new Error('Failed to fetch overview data')
    return response.json()
  }

  // Fetch timeline data
  async fetchTimelineData() {
    const response = await fetch(`/api/analytics/timeline?days=${this.dateRange}`)
    if (!response.ok) throw new Error('Failed to fetch timeline data')
    return response.json()
  }

  // Fetch user activity data
  async fetchUserActivityData() {
    const response = await fetch(`/api/analytics/user-activity?days=${this.dateRange}`)
    if (!response.ok) throw new Error('Failed to fetch user activity data')
    return response.json()
  }

  // Fetch message types data
  async fetchMessageTypesData() {
    const response = await fetch(`/api/analytics/message-types?days=${this.dateRange}`)
    if (!response.ok) throw new Error('Failed to fetch message types data')
    return response.json()
  }

  // Fetch response time data
  async fetchResponseTimeData() {
    const response = await fetch(`/api/analytics/response-time?days=${this.dateRange}`)
    if (!response.ok) throw new Error('Failed to fetch response time data')
    return response.json()
  }

  // Fetch top users data
  async fetchTopUsersData() {
    const response = await fetch(`/api/analytics/top-users?days=${this.dateRange}&limit=10`)
    if (!response.ok) throw new Error('Failed to fetch top users data')
    return response.json()
  }

  // Continue in next part...
}

// Export
window.AnalyticsDashboard = AnalyticsDashboard

  // ===== KPI Updates =====
  
  updateKPICards(data) {
    // Total Messages
    this.updateKPI('kpi-total-messages', data.total_messages, data.messages_trend)
    
    // Active Users
    this.updateKPI('kpi-active-users', data.active_users, data.users_trend)
    
    // Response Time
    const avgResponse = this.formatDuration(data.avg_response_time)
    this.updateKPI('kpi-response-time', avgResponse, data.response_trend)
    
    // Resolution Rate
    const resolutionRate = `${data.resolution_rate}%`
    this.updateKPI('kpi-resolution-rate', resolutionRate, data.resolution_trend)
  }

  updateKPI(elementId, value, trend) {
    const valueEl = document.getElementById(elementId)
    const trendEl = document.getElementById(`${elementId.replace('kpi-', 'kpi-')}-trend`)
    
    if (valueEl) {
      valueEl.innerHTML = `<span class="text-2xl font-bold">${value}</span>`
    }
    
    if (trendEl && trend) {
      const isPositive = trend.value >= 0
      const icon = isPositive ? 'trending-up' : 'trending-down'
      const color = isPositive ? 'text-green-500' : 'text-red-500'
      
      trendEl.innerHTML = `
        <i data-lucide="${icon}" class="w-4 h-4 ${color}"></i>
        <span class="${color} text-sm font-medium">${Math.abs(trend.value)}%</span>
        <span class="text-xs text-gray-500">${trend.label}</span>
      `
      lucide.createIcons()
    }
  }

  // ===== Chart Rendering =====
  
  renderCharts() {
    this.renderTimelineChart()
    this.renderMessageTypesChart()
    this.renderActivityHeatmap()
    this.renderResponseTimeChart()
  }

  renderTimelineChart() {
    const ctx = document.getElementById('timeline-chart')?.getContext('2d')
    if (!ctx) return

    // Destroy existing chart
    if (this.charts.has('timeline')) {
      this.charts.get('timeline').destroy()
    }

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.data.timeline.labels,
        datasets: [
          {
            label: 'User Messages',
            data: this.data.timeline.user_messages,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.1
          },
          {
            label: 'Bot Messages',
            data: this.data.timeline.bot_messages,
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.1
          },
          {
            label: 'Admin Messages',
            data: this.data.timeline.admin_messages,
            borderColor: 'rgb(251, 146, 60)',
            backgroundColor: 'rgba(251, 146, 60, 0.1)',
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })

    this.charts.set('timeline', chart)
  }

  renderMessageTypesChart() {
    const ctx = document.getElementById('message-types-chart')?.getContext('2d')
    if (!ctx) return

    if (this.charts.has('messageTypes')) {
      this.charts.get('messageTypes').destroy()
    }

    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['User Messages', 'Bot Messages', 'Admin Messages'],
        datasets: [{
          data: [
            this.data.messageTypes.user,
            this.data.messageTypes.bot,
            this.data.messageTypes.admin
          ],
          backgroundColor: [
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(251, 146, 60)'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.label}: ${context.parsed} (${percentage}%)`
              }
            }
          }
        }
      }
    })

    this.charts.set('messageTypes', chart)
  }

  renderActivityHeatmap() {
    const ctx = document.getElementById('activity-heatmap')?.getContext('2d')
    if (!ctx) return

    if (this.charts.has('heatmap')) {
      this.charts.get('heatmap').destroy()
    }

    // Create heatmap data
    const heatmapData = this.processHeatmapData(this.data.userActivity)

    const chart = new Chart(ctx, {
      type: 'matrix',
      data: {
        datasets: [{
          label: 'User Activity',
          data: heatmapData,
          backgroundColor(context) {
            const value = context.dataset.data[context.dataIndex].v
            const alpha = value / 100
            return `rgba(59, 130, 246, ${alpha})`
          },
          borderWidth: 1,
          borderColor: 'white',
          width: ({ chart }) => (chart.chartArea || {}).width / 7 - 1,
          height: ({ chart }) => (chart.chartArea || {}).height / 24 - 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              title: () => '',
              label: (context) => {
                const hour = context.dataset.data[context.dataIndex].y
                const day = context.dataset.data[context.dataIndex].x
                const value = context.dataset.data[context.dataIndex].v
                return `${this.getDayName(day)} ${hour}:00 - ${value} messages`
              }
            }
          }
        },
        scales: {
          x: {
            type: 'category',
            labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            offset: true,
            grid: {
              display: false
            }
          },
          y: {
            type: 'category',
            labels: Array.from({ length: 24 }, (_, i) => i),
            offset: true,
            grid: {
              display: false
            }
          }
        }
      }
    })

    this.charts.set('heatmap', chart)
  }

  renderResponseTimeChart() {
    const ctx = document.getElementById('response-time-chart')?.getContext('2d')
    if (!ctx) return

    if (this.charts.has('responseTime')) {
      this.charts.get('responseTime').destroy()
    }

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: this.data.responseTime.labels,
        datasets: [{
          label: 'Average Response Time (seconds)',
          data: this.data.responseTime.values,
          backgroundColor: 'rgba(139, 92, 246, 0.5)',
          borderColor: 'rgb(139, 92, 246)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Seconds'
            }
          }
        }
      }
    })

    this.charts.set('responseTime', chart)
  }

  // ===== Table Updates =====
  
  updateTables() {
    this.updateTopUsersTable()
    this.updateActivityLog()
  }

  updateTopUsersTable() {
    const tbody = document.getElementById('top-users-tbody')
    if (!tbody || !this.data.topUsers) return

    tbody.innerHTML = this.data.topUsers.map(user => `
      <tr>
        <td>
          <div class="flex items-center">
            <img src="${user.avatar || '/default-avatar.png'}" 
                 class="w-8 h-8 rounded-full mr-2" 
                 onerror="this.src='/default-avatar.png'">
            <span>${user.display_name}</span>
          </div>
        </td>
        <td>${user.message_count}</td>
        <td>${this.formatTime(user.last_active)}</td>
        <td>
          <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
            ${user.is_active ? 'Active' : 'Inactive'}
          </span>
        </td>
      </tr>
    `).join('')
  }

  updateActivityLog() {
    const activityLog = document.getElementById('activity-log')
    if (!activityLog) return

    // Simulated activity log - replace with real data
    const activities = [
      { type: 'message', user: 'John Doe', action: 'sent a message', time: '2 min ago' },
      { type: 'bot', user: 'Bot', action: 'responded to query', time: '5 min ago' },
      { type: 'admin', user: 'Admin', action: 'marked chat as resolved', time: '10 min ago' },
      { type: 'user', user: 'Jane Smith', action: 'started new conversation', time: '15 min ago' }
    ]

    activityLog.innerHTML = activities.map(activity => `
      <div class="activity-item">
        <div class="activity-icon ${activity.type}">
          <i data-lucide="${this.getActivityIcon(activity.type)}" class="w-4 h-4"></i>
        </div>
        <div class="activity-content">
          <div class="activity-text">
            <strong>${activity.user}</strong> ${activity.action}
          </div>
          <div class="activity-time">${activity.time}</div>
        </div>
      </div>
    `).join('')

    lucide.createIcons()
  }

  // ===== Utility Functions =====
  
  formatDuration(seconds) {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    return `${Math.floor(seconds / 3600)}h`
  }

  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`

    return date.toLocaleDateString('th-TH')
  }

  getDayName(index) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return days[index]
  }

  getActivityIcon(type) {
    const icons = {
      message: 'message-square',
      bot: 'bot',
      admin: 'user-check',
      user: 'user'
    }
    return icons[type] || 'circle'
  }

  processHeatmapData(data) {
    // Convert activity data to heatmap format
    const processed = []
    for (let day = 0; day < 7; day++) {
      for (let hour = 0; hour < 24; hour++) {
        processed.push({
          x: day,
          y: hour,
          v: data[day]?.[hour] || 0
        })
      }
    }
    return processed
  }

  // ===== Auto Refresh =====
  
  startAutoRefresh() {
    // Refresh every 5 minutes
    this.refreshInterval = setInterval(() => {
      this.loadAllData()
    }, 300000)
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
      this.refreshInterval = null
    }
  }

  // ===== Export Functions =====
  
  async exportAnalyticsReport() {
    const format = await this.showExportDialog()
    if (!format) return

    try {
      if (format === 'pdf') {
        await this.exportAsPDF()
      } else if (format === 'excel') {
        await this.exportAsExcel()
      }
      
      this.showNotification('Report exported successfully!', 'success')
    } catch (error) {
      this.showNotification('Export failed: ' + error.message, 'error')
    }
  }

  async showExportDialog() {
    return new Promise(resolve => {
      const dialog = document.createElement('div')
      dialog.className = 'dialog-overlay'
      dialog.innerHTML = `
        <div class="dialog-content">
          <h3 class="text-lg font-semibold mb-4">Export Analytics Report</h3>
          <p class="mb-4">Choose export format:</p>
          <div class="flex gap-2">
            <button onclick="resolve('pdf')" class="btn-primary">PDF Report</button>
            <button onclick="resolve('excel')" class="btn-primary">Excel Report</button>
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

  // ===== Loading States =====
  
  showLoadingState() {
    document.querySelectorAll('.skeleton-loader').forEach(el => {
      el.style.display = 'block'
    })
  }

  hideLoadingState() {
    document.querySelectorAll('.skeleton-loader').forEach(el => {
      el.style.display = 'none'
    })
  }

  showError(message) {
    this.showNotification(message, 'error')
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

  // Cleanup
  destroy() {
    this.stopAutoRefresh()
    this.charts.forEach(chart => chart.destroy())
    this.charts.clear()
  }
