const form = document.getElementById("chat-form")
form.addEventListener("submit", (e) => {
  e.preventDefault()
  const input = document.getElementById("chat-input")
  if (input.value && selectedUser) {
    ws.send(
      JSON.stringify({
        type: "send_message",
        user_id: selectedUser,
        message: input.value,
      })
    )
    appendMessage(input.value, false)
    input.value = ""
  }
})

// Loading Animation Functions
async function startLoading(userId, seconds = 20) {
  try {
    const response = await fetch(`/api/loading/start/${userId}?loading_seconds=${seconds}`, {
      method: 'POST'
    })
    const result = await response.json()
    console.log('Loading started:', result)
    return result.status === 'success'
  } catch (error) {
    console.error('Error starting loading:', error)
    return false
  }
}

async function stopLoading(userId) {
  try {
    const response = await fetch(`/api/loading/stop/${userId}`, {
      method: 'POST'
    })
    const result = await response.json()
    console.log('Loading stopped:', result)
    return result.status === 'success'
  } catch (error) {
    console.error('Error stopping loading:', error)
    return false
  }
}

// Add loading control buttons
function addLoadingControls() {
  const chatActions = document.querySelector('.chat-actions')
  if (chatActions && !document.getElementById('loading-controls')) {
    const loadingControls = document.createElement('div')
    loadingControls.id = 'loading-controls'
    loadingControls.className = 'flex gap-2 mt-2'
    loadingControls.innerHTML = `
      <button id="start-loading-btn" class="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600">
        <i data-lucide="loader"></i> Start Typing
      </button>
      <button id="stop-loading-btn" class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600">
        <i data-lucide="square"></i> Stop Typing
      </button>
    `
    chatActions.appendChild(loadingControls)
    
    // Add event listeners
    document.getElementById('start-loading-btn').addEventListener('click', () => {
      if (selectedUser) {
        startLoading(selectedUser, 30)  // 30 seconds loading
      }
    })
    
    document.getElementById('stop-loading-btn').addEventListener('click', () => {
      if (selectedUser) {
        stopLoading(selectedUser)
      }
    })
    
    // Initialize icons
    lucide.createIcons()
  }
}

// Export functions for use in main.js
window.startLoading = startLoading
window.stopLoading = stopLoading
window.addLoadingControls = addLoadingControls
