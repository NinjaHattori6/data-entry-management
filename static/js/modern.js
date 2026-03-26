// ===================================
// ONCOBLOOM - Modern JavaScript
// ===================================

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
});

// Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
    
    // Remove on click
    toast.addEventListener('click', function() {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
}

function getToastIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'danger': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

// Modal Functions
function showModal(title, message, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalConfirm = document.getElementById('modalConfirm');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    modalConfirm.onclick = function() {
        if (onConfirm) onConfirm();
        closeModal();
    };
    
    modal.classList.add('show');
}

function closeModal() {
    const modal = document.getElementById('confirmModal');
    modal.classList.remove('show');
}

// Enhanced Confirm Dialog
function confirmAction(message, onConfirm) {
    showModal('Confirm Action', message, onConfirm);
}

// Form Validation
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'This field is required');
            isValid = false;
        } else {
            clearError(input);
        }
    });
    
    return isValid;
}

function showError(input, message) {
    clearError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = 'var(--danger)';
    errorDiv.style.fontSize = 'var(--font-size-sm)';
    errorDiv.style.marginTop = 'var(--spacing-xs)';
    
    input.style.borderColor = 'var(--danger)';
    input.parentNode.appendChild(errorDiv);
}

function clearError(input) {
    input.style.borderColor = '';
    const errorMessage = input.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Loading States
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner"></span> Loading...';
    button.disabled = true;
    button.dataset.originalText = originalText;
}

function hideLoading(button) {
    button.innerHTML = button.dataset.originalText;
    button.disabled = false;
    delete button.dataset.originalText;
}

// Enhanced Button Interactions
function initButtonInteractions() {
    // Add ripple effect to landing page buttons
    const buttons = document.querySelectorAll('.main-content.landing-page .navbar .btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.6)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple-animation 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            // Add ripple to button
            this.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Initialize button interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initButtonInteractions();
});

// Enhanced Search Functionality
function initEnhancedSearch(searchInput, options = {}) {
    const {
        minLength = 2,
        debounceMs = 300,
        showResults = false,
        clearButton = false
    } = options;
    
    let searchTimeout;
    let clearBtn;
    
    // Add clear button if enabled
    if (clearButton) {
        addClearButton(searchInput);
    }
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        // Show/hide clear button
        if (clearButton && clearBtn) {
            clearBtn.classList.toggle('show', query.length > 0);
        }
        
        // Debounce search
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (query.length >= minLength) {
                performSearch(query, searchInput);
            } else if (query.length === 0) {
                clearSearchResults(searchInput);
            }
        }, debounceMs);
    });
    
    // Handle Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = this.value.trim();
            if (query.length >= minLength) {
                performSearch(query, searchInput);
            }
        }
    });
    
    // Add loading state
    searchInput.addEventListener('search', function() {
        showSearchLoading(searchInput, true);
    });
    
    searchInput.addEventListener('search', function() {
        showSearchLoading(searchInput, false);
    });
}

function addClearButton(searchInput) {
    const clearBtn = document.createElement('button');
    clearBtn.className = 'search-clear';
    clearBtn.innerHTML = '×';
    clearBtn.type = 'button';
    clearBtn.setAttribute('aria-label', 'Clear search');
    
    searchInput.parentNode.appendChild(clearBtn);
    
    clearBtn.addEventListener('click', function() {
        searchInput.value = '';
        searchInput.focus();
        clearSearchResults(searchInput);
        this.classList.remove('show');
    });
    
    return clearBtn;
}

function showSearchLoading(searchInput, show) {
    let loading = searchInput.parentNode.querySelector('.search-loading');
    
    if (show && !loading) {
        loading = document.createElement('div');
        loading.className = 'search-loading';
        searchInput.parentNode.appendChild(loading);
    } else if (!show && loading) {
        loading.remove();
    }
}

function performSearch(query, searchInput) {
    // Show loading state
    showSearchLoading(searchInput, true);
    
    // Simulate search API call
    setTimeout(() => {
        showSearchLoading(searchInput, false);
        // Here you would typically make an API call
        console.log('Searching for:', query);
        
        // Show success feedback
        searchInput.classList.add('valid');
        setTimeout(() => {
            searchInput.classList.remove('valid');
        }, 1000);
    }, 500);
}

function clearSearchResults(searchInput) {
    // Clear any search results
    const results = searchInput.parentNode.querySelector('.search-results');
    if (results) {
        results.classList.remove('show');
    }
    
    // Remove validation state
    searchInput.classList.remove('valid', 'invalid');
}

// Initialize enhanced search for all search inputs
document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        // Determine context based on parent classes
        let options = {
            minLength: 2,
            debounceMs: 300,
            clearButton: true
        };
        
        // Context-specific options
        if (input.closest('.filter-search')) {
            options.minLength = 1;
            options.debounceMs = 200;
        }
        
        if (input.closest('.dashboard-search')) {
            options.minLength = 3;
            options.debounceMs = 400;
        }
        
        if (input.closest('.advanced-search')) {
            options.minLength = 2;
            options.debounceMs = 500;
            options.showResults = true;
        }
        
        initEnhancedSearch(input, options);
    });
    
    // Initialize search functionality for existing search bars
    const searchBars = document.querySelectorAll('.search-bar');
    searchBars.forEach(bar => {
        const input = bar.querySelector('.search-input');
        if (input) {
            initEnhancedSearch(input);
        }
    });
});

// Search results dropdown functionality
function showSearchResults(results, searchInput) {
    let resultsDropdown = searchInput.parentNode.querySelector('.search-results');
    
    if (!resultsDropdown) {
        resultsDropdown = document.createElement('div');
        resultsDropdown.className = 'search-results';
        searchInput.parentNode.appendChild(resultsDropdown);
    }
    
    // Clear existing results
    resultsDropdown.innerHTML = '';
    
    if (results.length === 0) {
        resultsDropdown.innerHTML = `
            <div class="search-result-item">
                <div class="search-result-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="search-result-text">
                    No results found
                    <div class="search-result-subtext">Try a different search term</div>
                </div>
            </div>
        `;
    } else {
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <div class="search-result-icon">
                    <i class="fas fa-${result.icon || 'user'}"></i>
                </div>
                <div class="search-result-text">
                    ${result.text}
                    ${result.subtext ? `<div class="search-result-subtext">${result.subtext}</div>` : ''}
                </div>
            `;
            
            item.addEventListener('click', () => {
                if (result.onClick) {
                    result.onClick();
                }
                resultsDropdown.classList.remove('show');
            });
            
            resultsDropdown.appendChild(item);
        });
    }
    
    resultsDropdown.classList.add('show');
}

// Close search results when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-bar')) {
        const results = document.querySelectorAll('.search-results.show');
        results.forEach(result => {
            result.classList.remove('show');
        });
    }
});

// Enhanced search filter functionality
function initSearchFilter(searchInput, tableRows) {
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const shouldShow = searchTerm === '' || text.includes(searchTerm);
            row.style.display = shouldShow ? '' : 'none';
            
            // Add animation class
            if (shouldShow) {
                row.style.animation = 'fadeIn 0.3s ease';
            }
        });
    });
}

// Advanced search with multiple filters
function initAdvancedSearch(searchInput, filters = {}) {
    let searchTimeout;
    
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                performAdvancedSearch(query, filters);
            } else {
                clearAdvancedSearch();
            }
        }, 300);
    });
}

function performAdvancedSearch(query, filters) {
    // Implementation for advanced search with multiple filters
    console.log('Advanced search:', query, filters);
    // This would typically make an API call with filters
}

function clearAdvancedSearch() {
    // Clear advanced search results
    console.log('Clearing advanced search');
}

// Search analytics
function trackSearch(query, resultsCount, context = 'general') {
    // Track search analytics
    console.log('Search tracked:', {
        query,
        resultsCount,
        context,
        timestamp: new Date().toISOString()
    });
}

// Auto-complete functionality
function initAutoComplete(searchInput, suggestions = []) {
    let currentFocus = -1;
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        
        if (query.length < 2) {
            hideAutoComplete(searchInput);
            return;
        }
        
        const filteredSuggestions = suggestions.filter(s => 
            s.toLowerCase().includes(query)
        );
        
        showAutoComplete(searchInput, filteredSuggestions);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        const dropdown = searchInput.parentNode.querySelector('.search-results');
        const items = dropdown ? dropdown.querySelectorAll('.search-result-item') : [];
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus = Math.min(currentFocus + 1, items.length - 1);
            updateAutoCompleteFocus(items, currentFocus);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus = Math.max(currentFocus - 1, -1);
            updateAutoCompleteFocus(items, currentFocus);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus >= 0 && items[currentFocus]) {
                items[currentFocus].click();
            }
        } else if (e.key === 'Escape') {
            hideAutoComplete(searchInput);
        }
    });
}

function showAutoComplete(searchInput, suggestions) {
    const results = suggestions.map(suggestion => ({
        text: suggestion.text || suggestion,
        subtext: suggestion.subtext || '',
        icon: suggestion.icon || 'search',
        onClick: () => {
            searchInput.value = suggestion.text || suggestion;
            hideAutoComplete(searchInput);
            performSearch(suggestion.text || suggestion, searchInput);
        }
    }));
    
    showSearchResults(results, searchInput);
}

function hideAutoComplete(searchInput) {
    const dropdown = searchInput.parentNode.querySelector('.search-results');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
}

function updateAutoCompleteFocus(items, index) {
    items.forEach((item, i) => {
        if (i === index) {
            item.style.background = 'var(--background)';
            item.style.fontWeight = '600';
        } else {
            item.style.background = '';
            item.style.fontWeight = '500';
        }
    });
}

// Table Sorting
function initTableSort(table) {
    const headers = table.querySelectorAll('th[data-sort]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const column = this.dataset.sort;
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                const aText = a.querySelector(`td[data-column="${column}"]`).textContent;
                const bText = b.querySelector(`td[data-column="${column}"]`).textContent;
                return aText.localeCompare(bText);
            });
            
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Export Functions
function exportData(format, filters = {}) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/export_data';
    
    // Add format
    const formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'format';
    formatInput.value = format;
    form.appendChild(formatInput);
    
    // Add filters
    Object.keys(filters).forEach(key => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = filters[key];
        form.appendChild(input);
    });
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

// Chart Helper Functions
function createDoughnutChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    }
                }
            },
            ...options
        }
    });
}

function createBarChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'bar',
        data: data,
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
                    grid: {
                        borderDash: [2, 2]
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            ...options
        }
    });
}

// Password Toggle
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize all auto-resizing textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        autoResize(textarea);
        textarea.addEventListener('input', () => autoResize(textarea));
    });
});

// Smooth scroll
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'danger');
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format number
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: var(--secondary);
                color: white;
                padding: var(--spacing-sm) var(--spacing-md);
                border-radius: var(--radius-sm);
                font-size: var(--font-size-xs);
                z-index: 10000;
                pointer-events: none;
                white-space: nowrap;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            
            this.tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    
    // Add slide out animation for toasts
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showToast('An unexpected error occurred', 'danger');
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('An unexpected error occurred', 'danger');
});
