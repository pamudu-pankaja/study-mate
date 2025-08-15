// Main function to show alerts - THIS IS THE LINE YOU'LL USE MOST
function showAlert(type, title, message, duration = 5000) {
    const container = document.getElementById('alert-container');
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    
    alert.innerHTML = `
        <div class="alert-icon"></div>
        <div class="alert-content">
            <div class="alert-title">${title}</div>
            <div class="alert-message">${message}</div>
        </div>
        <button class="alert-close" onclick="closeAlert(this)">×</button>
    `;
    
    // Add to container
    container.appendChild(alert);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            closeAlert(alert.querySelector('.alert-close'));
        }, duration);
    }
}

// Function to close individual alert
function closeAlert(closeBtn) {
    const alert = closeBtn.closest('.alert');
    alert.classList.add('removing');
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 300);
}

// Convenience functions - USE THESE IN YOUR CODE
function showSuccess(title = 'Success', message = 'Your operation was successful!') {
    showAlert('success', title, message);
}

function showInfo(title = 'Info', message = 'Be Notice!') {
    showAlert('info', title, message);
}

function showError(title = 'Error', message = 'Something went wrong.') {
    showAlert('error', title, message);
}

function showWarning(title = 'Are you sure?', message = 'This action cannot be undone.') {
    showAlert('warning', title, message);
}

// Clear all alerts
function clearAllAlerts() {
    const container = document.getElementById('alert-container');
    container.innerHTML = '';
}

// EXAMPLES OF HOW TO TRIGGER ALERTS IN YOUR CODE:
// showSuccess('File Uploaded', 'Your PDF has been successfully imported!');
// showError('Upload Failed', 'Please select a valid PDF file.');
// showInfo('Processing', 'Your file is being processed...');
// showWarning('Delete Book', 'This will permanently delete the saved book you wont be able to use it again are you sure you want to do this ')