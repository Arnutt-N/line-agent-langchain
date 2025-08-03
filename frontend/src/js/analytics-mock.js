// ===== Analytics Mock Data Generator =====
// Generate mock data for testing analytics dashboard

class AnalyticsMockData {
  // Generate overview data
  static generateOverviewData(days = 30) {
    const baseMessages = 1000
    const baseUsers = 50
    
    return {
      total_messages: baseMessages + Math.floor(Math.random() * 500),
      messages_trend: {
        value: Math.floor(Math.random() * 30) - 15,
        label: 'vs last period'
      },
      active_users: baseUsers + Math.floor(Math.random() * 20),
      users_trend: {
        value: Math.floor(Math.random() * 20) - 10,
        label: 'vs last period'
      },
      avg_response_time: Math.floor(Math.random() * 300) + 30, // 30-330 seconds
      response_trend: {
        value: Math.floor(Math.random() * 20) - 10,
        label: 'vs last period'
      },
      resolution_rate: Math.floor(Math.random() * 30) + 70, // 70-100%
      resolution_trend: {
        value: Math.floor(Math.random() * 10) - 5,
        label: 'vs last period'
      }
    }
  }

  // Generate timeline data
  static generateTimelineData(days = 30) {
    const labels = []
    const userMessages = []
    const botMessages = []
    const adminMessages = []
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      labels.push(date.toLocaleDateString('th-TH', { month: 'short', day: 'numeric' }))
      
      userMessages.push(Math.floor(Math.random() * 100) + 20)
      botMessages.push(Math.floor(Math.random() * 80) + 10)
      adminMessages.push(Math.floor(Math.random() * 30) + 5)
    }
    
    return {
      labels,
      user_messages: userMessages,
      bot_messages: botMessages,
      admin_messages: adminMessages
    }
  }

  // Generate user activity heatmap data
  static generateUserActivityData() {
    const data = []
    
    for (let day = 0; day < 7; day++) {
      data[day] = []
      for (let hour = 0; hour < 24; hour++) {
        // Peak hours: 9-11, 14-16, 19-21
        let activity = Math.floor(Math.random() * 20)
        if ((hour >= 9 && hour <= 11) || (hour >= 14 && hour <= 16) || (hour >= 19 && hour <= 21)) {
          activity = Math.floor(Math.random() * 80) + 20
        }
        data[day][hour] = activity
      }
    }
    
    return data
  }

  // Generate message types data
  static generateMessageTypesData() {
    const total = 1000
    const userPercent = 0.5 + Math.random() * 0.2
    const botPercent = 0.3 + Math.random() * 0.1
    const adminPercent = 1 - userPercent - botPercent
    
    return {
      user: Math.floor(total * userPercent),
      bot: Math.floor(total * botPercent),
      admin: Math.floor(total * adminPercent)
    }
  }

  // Generate response time data
  static generateResponseTimeData(days = 7) {
    const labels = []
    const values = []
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      labels.push(date.toLocaleDateString('th-TH', { weekday: 'short' }))
      
      // Response time in seconds (30-300)
      values.push(Math.floor(Math.random() * 270) + 30)
    }
    
    return { labels, values }
  }

  // Generate top users data
  static generateTopUsersData(limit = 10) {
    const users = []
    const names = [
      'สมชาย ใจดี', 'สมหญิง รักสงบ', 'วิชัย มั่นคง', 'นภา สว่างใส',
      'ประภาส แสงทอง', 'มานพ ขยันทำ', 'สุดา เก่งกาจ', 'อนันต์ ยิ้มแย้ม',
      'พิมพ์ใจ หวานเย็น', 'ธนา รวยทรัพย์'
    ]
    
    for (let i = 0; i < limit; i++) {
      users.push({
        user_id: `U${Math.random().toString(36).substr(2, 9)}`,
        display_name: names[i] || `User ${i + 1}`,
        avatar: Math.random() > 0.3 ? `https://i.pravatar.cc/150?img=${i + 1}` : null,
        message_count: Math.floor(Math.random() * 200) + 10,
        last_active: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        is_active: Math.random() > 0.3
      })
    }
    
    return users.sort((a, b) => b.message_count - a.message_count)
  }

  // Mock API endpoints
  static setupMockEndpoints() {
    // Override fetch for analytics endpoints
    const originalFetch = window.fetch
    
    window.fetch = async (url, options) => {
      // Check if it's an analytics endpoint
      if (url.includes('/api/analytics/')) {
        return this.handleMockRequest(url)
      }
      
      // Otherwise use original fetch
      return originalFetch(url, options)
    }
  }

  static async handleMockRequest(url) {
    // Extract endpoint and params
    const urlObj = new URL(url, window.location.origin)
    const endpoint = urlObj.pathname.split('/').pop()
    const days = parseInt(urlObj.searchParams.get('days') || '30')
    
    let data
    
    switch (endpoint) {
      case 'overview':
        data = this.generateOverviewData(days)
        break
      case 'timeline':
        data = this.generateTimelineData(days)
        break
      case 'user-activity':
        data = this.generateUserActivityData()
        break
      case 'message-types':
        data = this.generateMessageTypesData()
        break
      case 'response-time':
        data = this.generateResponseTimeData(Math.min(days, 7))
        break
      case 'top-users':
        const limit = parseInt(urlObj.searchParams.get('limit') || '10')
        data = this.generateTopUsersData(limit)
        break
      default:
        data = {}
    }
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200))
    
    // Return mock response
    return {
      ok: true,
      status: 200,
      json: async () => data
    }
  }
}

// Auto-setup mock endpoints if in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  AnalyticsMockData.setupMockEndpoints()
  console.log('📊 Analytics mock data enabled')
}

// Export
window.AnalyticsMockData = AnalyticsMockData
