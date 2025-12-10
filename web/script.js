// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const sampleBtn = document.getElementById('sampleBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('resultsSection');
const routeBadge = document.getElementById('routeBadge');
const reasoning = document.getElementById('reasoning');
const fieldsGrid = document.getElementById('fieldsGrid');
const missingFieldsCard = document.getElementById('missingFieldsCard');
const missingFields = document.getElementById('missingFields');
const jsonOutput = document.getElementById('jsonOutput');
const copyBtn = document.getElementById('copyBtn');

let selectedFile = null;

// Upload Area Events
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['.pdf', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExt)) {
        alert('Please select a PDF or TXT file.');
        return;
    }

    selectedFile = file;

    // Update upload area
    const uploadContent = uploadArea.querySelector('.upload-content');
    uploadContent.innerHTML = `
        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="color: var(--success);">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3>✓ ${file.name}</h3>
        <p>${formatFileSize(file.size)} • Ready to process</p>
    `;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Upload Button
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a file first.');
        return;
    }

    await processDocument(selectedFile);
});

// Sample Button
sampleBtn.addEventListener('click', async () => {
    // Use claim_001.txt as sample
    const samplePath = 'sample_documents/claim_001.txt';

    try {
        const response = await fetch(`/${samplePath}`);
        const text = await response.text();

        // Create a blob and process it
        const blob = new Blob([text], { type: 'text/plain' });
        const file = new File([blob], 'claim_001.txt', { type: 'text/plain' });

        handleFileSelect(file);
        await processDocument(file);
    } catch (error) {
        console.error('Error loading sample:', error);
        alert('Could not load sample document. Try uploading your own file.');
    }
});

// Process Document
async function processDocument(file) {
    // Show loading
    loadingOverlay.classList.add('active');
    resultsSection.style.display = 'none';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        // Send to API
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed');
        }

        const result = await response.json();

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);
        alert(`Error processing document: ${error.message}\n\nMake sure you have set up your GEMINI_API_KEY in the .env file.`);
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

// Display Results
function displayResults(result) {
    // Show results section
    resultsSection.style.display = 'block';

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Display routing result
    displayRouting(result.recommendedRoute, result.reasoning);

    // Display extracted fields
    displayFields(result.extractedFields);

    // Display missing fields
    displayMissingFields(result.missingFields);

    // Display JSON output
    jsonOutput.textContent = JSON.stringify(result, null, 2);
}

// Display Routing
function displayRouting(route, reasoningText) {
    // Set badge
    routeBadge.textContent = route;
    routeBadge.className = 'route-badge';

    // Add appropriate class
    const routeClass = route.toLowerCase().replace(/\s+/g, '-');
    routeBadge.classList.add(routeClass);

    // Set reasoning
    reasoning.textContent = reasoningText;
}

// Display Fields
function displayFields(fields) {
    fieldsGrid.innerHTML = '';

    // Flatten nested objects
    const flatFields = flattenObject(fields);

    // Sort fields
    const sortedFields = Object.entries(flatFields).sort((a, b) =>
        a[0].localeCompare(b[0])
    );

    // Create field items
    sortedFields.forEach(([key, value]) => {
        const fieldItem = document.createElement('div');
        fieldItem.className = 'field-item';

        const label = document.createElement('div');
        label.className = 'field-label';
        label.textContent = formatFieldName(key);

        const valueDiv = document.createElement('div');
        valueDiv.className = 'field-value';

        if (value === null || value === undefined) {
            valueDiv.textContent = 'Not provided';
            valueDiv.classList.add('null');
        } else if (Array.isArray(value)) {
            valueDiv.textContent = value.length > 0 ? value.join(', ') : 'None';
        } else if (typeof value === 'object') {
            valueDiv.textContent = JSON.stringify(value);
        } else {
            valueDiv.textContent = value;
        }

        fieldItem.appendChild(label);
        fieldItem.appendChild(valueDiv);
        fieldsGrid.appendChild(fieldItem);
    });
}

// Display Missing Fields
function displayMissingFields(fields) {
    if (fields.length === 0) {
        missingFieldsCard.style.display = 'none';
        return;
    }

    missingFieldsCard.style.display = 'block';
    missingFields.innerHTML = '';

    fields.forEach(field => {
        const tag = document.createElement('div');
        tag.className = 'missing-field-tag';
        tag.textContent = formatFieldName(field);
        missingFields.appendChild(tag);
    });
}

// Utility Functions
function flattenObject(obj, prefix = '') {
    const flattened = {};

    for (const [key, value] of Object.entries(obj)) {
        const newKey = prefix ? `${prefix}.${key}` : key;

        if (value && typeof value === 'object' && !Array.isArray(value)) {
            Object.assign(flattened, flattenObject(value, newKey));
        } else {
            flattened[newKey] = value;
        }
    }

    return flattened;
}

function formatFieldName(fieldPath) {
    // Convert camelCase and dot notation to readable format
    return fieldPath
        .split('.')
        .map(part => {
            // Convert camelCase to spaces
            const spaced = part.replace(/([A-Z])/g, ' $1').trim();
            // Capitalize first letter of each word
            return spaced.charAt(0).toUpperCase() + spaced.slice(1);
        })
        .join(' - ');
}

// Copy to Clipboard
copyBtn.addEventListener('click', () => {
    const text = jsonOutput.textContent;

    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
        }, 2000);
    }).catch(err => {
        alert('Failed to copy to clipboard');
    });
});

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    console.log('Insurance Claims Processing Agent loaded');
    loadConfigStatus();
});

// Settings Modal
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const removeApiKeyBtn = document.getElementById('removeApiKeyBtn');
const settingsAlert = document.getElementById('settingsAlert');
const configStatus = document.getElementById('configStatus');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Open settings
settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('active');
    apiKeyInput.focus();
});

// Close settings
modalCloseBtn.addEventListener('click', () => {
    settingsModal.classList.remove('active');
    hideAlert();
});

// Close on backdrop click
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.classList.remove('active');
        hideAlert();
    }
});

// Load configuration status
async function loadConfigStatus() {
    try {
        const response = await fetch('/config');
        const config = await response.json();

        if (config.using_gemini) {
            statusIndicator.className = 'status-indicator gemini';
            statusText.textContent = '🤖 Using Gemini AI';
        } else {
            statusIndicator.className = 'status-indicator fallback';
            statusText.textContent = '📦 Using Pattern-Based Extraction';
        }
    } catch (error) {
        console.error('Error loading config:', error);
        statusIndicator.className = 'status-indicator fallback';
        statusText.textContent = '⚠️ Configuration unavailable';
    }
}

// Save API key
saveApiKeyBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
        showAlert('Please enter an API key', 'error');
        return;
    }

    try {
        const response = await fetch('/config/api-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save API key');
        }

        const result = await response.json();

        showAlert(result.message, 'success');
        apiKeyInput.value = '';

        setTimeout(() => {
            settingsModal.classList.remove('active');
            hideAlert();
            loadConfigStatus();
        }, 2000);

    } catch (error) {
        console.error('Error saving API key:', error);
        showAlert(error.message, 'error');
    }
});

// Remove API key
removeApiKeyBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to remove the API key and use fallback extraction?')) {
        return;
    }

    try {
        const response = await fetch('/config/api-key', {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to remove API key');
        }

        const result = await response.json();

        showAlert(result.message, 'success');
        apiKeyInput.value = '';

        setTimeout(() => {
            settingsModal.classList.remove('active');
            hideAlert();
            loadConfigStatus();
        }, 2000);

    } catch (error) {
        console.error('Error removing API key:', error);
        showAlert(error.message, 'error');
    }
});

// Show alert
function showAlert(message, type) {
    settingsAlert.textContent = message;
    settingsAlert.className = `alert ${type}`;
    settingsAlert.style.display = 'block';
}

// Hide alert
function hideAlert() {
    settingsAlert.style.display = 'none';
    settingsAlert.className = 'alert';
}

