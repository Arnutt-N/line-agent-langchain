// Message Templates Management
// Frontend JavaScript for managing templates

class TemplateManager {
    constructor() {
        this.currentCategory = null
        this.currentTemplate = null
        this.categories = []
        this.templates = []
    }

    async init() {
        await this.loadCategories()
        await this.loadTemplates()
        this.setupEventListeners()
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories')
            this.categories = await response.json()
            this.renderCategories()
        } catch (error) {
            console.error('Error loading categories:', error)
        }
    }

    async loadTemplates(categoryId = null, messageType = null) {
        try {
            let url = '/api/templates?'
            if (categoryId) url += `category_id=${categoryId}&`
            if (messageType) url += `message_type=${messageType}&`
            
            const response = await fetch(url)
            this.templates = await response.json()
            this.renderTemplates()
        } catch (error) {
            console.error('Error loading templates:', error)
        }
    }

    renderCategories() {
        const container = document.getElementById('categories-list')
        if (!container) return

        container.innerHTML = this.categories.map(category => `
            <div class="category-item p-3 border rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" 
                 data-category-id="${category.id}">
                <div class="flex items-center">
                    <div class="w-4 h-4 rounded" style="background-color: ${category.color}"></div>
                    <span class="ml-2 font-medium">${category.name}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${category.description || ''}</p>
            </div>
        `).join('')

        // Add click listeners
        container.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', () => {
                const categoryId = parseInt(item.dataset.categoryId)
                this.selectCategory(categoryId)
            })
        })
    }

    renderTemplates() {
        const container = document.getElementById('templates-list')
        if (!container) return

        container.innerHTML = this.templates.map(template => `
            <div class="template-item p-4 border rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" 
                 data-template-id="${template.id}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h3 class="font-medium">${template.name}</h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400">${template.description || ''}</p>
                        <div class="flex items-center mt-2">
                            <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${template.message_type}</span>
                            <span class="ml-2 text-xs text-gray-500">Priority: ${template.priority}</span>
                            <span class="ml-2 text-xs text-gray-500">Used: ${template.usage_count} times</span>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button class="preview-btn text-blue-600 hover:text-blue-800" data-template-id="${template.id}">
                            <i data-lucide="eye"></i>
                        </button>
                        <button class="edit-btn text-green-600 hover:text-green-800" data-template-id="${template.id}">
                            <i data-lucide="edit"></i>
                        </button>
                        <button class="delete-btn text-red-600 hover:text-red-800" data-template-id="${template.id}">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('')

        // Initialize icons
        lucide.createIcons()
    }

    selectCategory(categoryId) {
        this.currentCategory = categoryId
        this.loadTemplates(categoryId)
        
        // Update UI
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('bg-blue-100', 'dark:bg-blue-800')
        })
        
        const selectedItem = document.querySelector(`[data-category-id="${categoryId}"]`)
        if (selectedItem) {
            selectedItem.classList.add('bg-blue-100', 'dark:bg-blue-800')
        }
    }

    setupEventListeners() {
        // Add new template button
        const addTemplateBtn = document.getElementById('add-template-btn')
        if (addTemplateBtn) {
            addTemplateBtn.addEventListener('click', () => this.showTemplateModal())
        }

        // Add new category button
        const addCategoryBtn = document.getElementById('add-category-btn')
        if (addCategoryBtn) {
            addCategoryBtn.addEventListener('click', () => this.showCategoryModal())
        }

        // Filter by message type
        const messageTypeFilter = document.getElementById('message-type-filter')
        if (messageTypeFilter) {
            messageTypeFilter.addEventListener('change', (e) => {
                this.loadTemplates(this.currentCategory, e.target.value || null)
            })
        }
    }

    showTemplateModal(templateId = null) {
        // TODO: Implement template creation/editing modal
        console.log('Show template modal for:', templateId)
    }

    showCategoryModal(categoryId = null) {
        // TODO: Implement category creation/editing modal
        console.log('Show category modal for:', categoryId)
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.templateManager = new TemplateManager()
    window.templateManager.init()
})
