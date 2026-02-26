// Main JavaScript file for Oncology Tracking System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize sidebar toggle
    initializeSidebar();
    
    // Initialize charts
    initializeCharts();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize data tables
    initializeDataTables();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Save sidebar state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }
    
    // Restore sidebar state from localStorage
    const sidebarState = localStorage.getItem('sidebarCollapsed');
    if (sidebarState === 'true') {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }
}

// Initialize Chart.js charts
function initializeCharts() {
    // Condition Distribution Doughnut Chart
    const conditionCtx = document.getElementById('conditionChart');
    if (conditionCtx) {
        new Chart(conditionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Lung Cancer', 'Breast Cancer', 'Prostate Cancer', 'Colon Cancer', 'Ovarian Cancer', 'Others'],
                datasets: [{
                    data: [30, 25, 20, 15, 7, 3],
                    backgroundColor: [
                        '#2c7a7b',
                        '#38a169',
                        '#ed8936',
                        '#e53e3e',
                        '#3182ce',
                        '#805ad5'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Status Distribution Doughnut Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Under Treatment', 'Remission', 'Relapse', 'Terminal'],
                datasets: [{
                    data: [45, 30, 20, 5],
                    backgroundColor: [
                        '#3182ce',
                        '#38a169',
                        '#ed8936',
                        '#e53e3e'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Monthly Trend Line Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'New Cases',
                    data: [12, 19, 15, 25, 22, 30, 28, 35, 32, 38, 42, 45],
                    borderColor: '#2c7a7b',
                    backgroundColor: 'rgba(44, 122, 123, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
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
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Initialize form validations
function initializeFormValidations() {
    // Patient form validation
    const patientForm = document.getElementById('patientForm');
    if (patientForm) {
        patientForm.addEventListener('submit', function(e) {
            if (!validatePatientForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Registration form validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegisterForm()) {
                e.preventDefault();
            }
        });
    }
}

// Validate patient form
function validatePatientForm() {
    const name = document.getElementById('name').value.trim();
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    const cancerType = document.getElementById('cancer_type').value;
    const status = document.getElementById('status').value;
    const diagnosisDate = document.getElementById('diagnosis_date').value;
    
    let isValid = true;
    
    // Reset previous error states
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    
    if (!name) {
        document.getElementById('name').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!age || age < 0 || age > 150) {
        document.getElementById('age').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!gender) {
        document.getElementById('gender').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!cancerType) {
        document.getElementById('cancer_type').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!status) {
        document.getElementById('status').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!diagnosisDate) {
        document.getElementById('diagnosis_date').classList.add('is-invalid');
        isValid = false;
    }
    
    return isValid;
}

// Validate registration form
function validateRegisterForm() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    let isValid = true;
    
    // Reset previous error states
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    
    if (!username || username.length < 3) {
        document.getElementById('username').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!email || !isValidEmail(email)) {
        document.getElementById('email').classList.add('is-invalid');
        isValid = false;
    }
    
    if (!password || password.length < 6) {
        document.getElementById('password').classList.add('is-invalid');
        isValid = false;
    }
    
    if (password !== confirmPassword) {
        document.getElementById('confirm_password').classList.add('is-invalid');
        isValid = false;
    }
    
    return isValid;
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Initialize data tables with search and sort functionality
function initializeDataTables() {
    const patientTable = document.getElementById('patientTable');
    if (patientTable) {
        // Add search functionality
        const searchInput = document.getElementById('tableSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = patientTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            });
        }
        
        // Add sort functionality
        const sortableHeaders = patientTable.querySelectorAll('th[data-sort]');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                const tbody = patientTable.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    const aText = a.children[column].textContent.trim();
                    const bText = b.children[column].textContent.trim();
                    
                    if (!isNaN(aText) && !isNaN(bText)) {
                        return parseFloat(aText) - parseFloat(bText);
                    }
                    
                    return aText.localeCompare(bText);
                });
                
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }
}

// Utility function to show loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    element.appendChild(spinner);
}

// Utility function to hide loading spinner
function hideLoading(element) {
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Utility function to show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Export data functionality
function exportData(format) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/export_data';
    
    const formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'format';
    formatInput.value = format;
    
    form.appendChild(formatInput);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

// Confirm delete action
function confirmDelete(id, name) {
    if (confirm(`Are you sure you want to delete patient "${name}"? This action cannot be undone.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete_record/${id}`;
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken.getAttribute('content');
            form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }
}

// Print functionality
function printTable() {
    const printContent = document.getElementById('patientTable').outerHTML;
    const originalContent = document.body.innerHTML;
    
    document.body.innerHTML = `
        <html>
            <head>
                <title>Patient Records</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h1>Patient Records</h1>
                ${printContent}
            </body>
        </html>
    `;
    
    window.print();
    document.body.innerHTML = originalContent;
    location.reload();
}
