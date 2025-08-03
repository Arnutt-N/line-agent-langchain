// ===== User Profile Management Module =====
// Enhanced user profile handling with real-time updates

class UserProfileManager {
  constructor() {
    this.profiles = new Map()
    this.defaultAvatar = '/default-avatar.png'
    this.cacheExpiry = 3600000 // 1 hour
  }

  // ดึงข้อมูล profile จาก LINE API
  async fetchUserProfile(userId) {
    try {
      const response = await fetch(`/api/users/${userId}/profile`)
      if (!response.ok) throw new Error('Failed to fetch profile')
      
      const data = await response.json()
      return {
        user_id: userId,
        display_name: data.displayName || `Customer ${userId.slice(-6)}`,
        picture_url: data.pictureUrl,
        status_message: data.statusMessage,
        language: data.language || 'th',
        source: 'api',
        fetched_at: new Date().toISOString()
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
      return this.getFallbackProfile(userId)
    }
  }

  // Fallback profile data
  getFallbackProfile(userId) {
    return {
      user_id: userId,
      display_name: `Customer ${userId.slice(-6)}`,
      picture_url: null,
      status_message: null,
      language: 'th',
      source: 'fallback',
      fetched_at: new Date().toISOString()
    }
  }

  // Get or create profile with caching
  async getProfile(userId, forceRefresh = false) {
    const cached = this.profiles.get(userId)
    
    // Check if cache is valid
    if (cached && !forceRefresh) {
      const cacheAge = Date.now() - new Date(cached.fetched_at).getTime()
      if (cacheAge < this.cacheExpiry) {
        return cached
      }
    }

    // Fetch fresh profile
    const profile = await this.fetchUserProfile(userId)
    this.profiles.set(userId, profile)
    return profile
  }

  // Update profile data
  updateProfile(userId, updates) {
    const profile = this.profiles.get(userId) || this.getFallbackProfile(userId)
    const updatedProfile = {
      ...profile,
      ...updates,
      updated_at: new Date().toISOString()
    }
    this.profiles.set(userId, updatedProfile)
    return updatedProfile
  }

  // Batch fetch profiles
  async fetchMultipleProfiles(userIds) {
    const promises = userIds.map(id => this.getProfile(id))
    return Promise.all(promises)
  }

  // Clear old cache entries
  cleanupCache() {
    const now = Date.now()
    for (const [userId, profile] of this.profiles.entries()) {
      const age = now - new Date(profile.fetched_at).getTime()
      if (age > this.cacheExpiry * 2) {
        this.profiles.delete(userId)
      }
    }
  }
}

// Export for use in main.js
window.UserProfileManager = UserProfileManager
