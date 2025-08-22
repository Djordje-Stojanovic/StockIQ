/**
 * StockIQ Main Frontend Application
 * Handles health check, ticker validation, and API communication
 */

class StockIQApp {
    constructor() {
        this.healthStatusEl = document.getElementById('health-status');
        this.tickerForm = document.getElementById('ticker-form');
        this.tickerInput = document.getElementById('ticker');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.resultsContainer = document.getElementById('results-container');
        this.errorEl = document.getElementById('ticker-error');
        this.feedbackEl = document.getElementById('ticker-feedback');
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    init() {
        this.checkHealth();
        this.setupEventListeners();
    }
    
    /**
     * Check application health status
     */
    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.healthStatusEl.innerHTML = `
                    <p><strong>Status:</strong> ${data.status}</p>
                    <p><strong>Service:</strong> ${data.service} v${data.version}</p>
                    <p><strong>OpenAI:</strong> ${data.openai_configured ? 'Configured' : 'Not Configured'}</p>
                `;
                this.healthStatusEl.className = 'status-healthy';
            } else {
                throw new Error('Service unhealthy');
            }
        } catch (error) {
            this.healthStatusEl.innerHTML = `
                <p><strong>Status:</strong> Error</p>
                <p><strong>Message:</strong> Unable to connect to StockIQ service</p>
            `;
            this.healthStatusEl.className = 'status-error';
        }
    }
    
    /**
     * Setup event listeners for user interactions
     */
    setupEventListeners() {
        this.tickerForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        this.tickerInput.addEventListener('input', () => this.validateTickerInput());
        this.tickerInput.addEventListener('blur', () => this.validateTickerInput());
    }
    
    /**
     * Validate ticker input in real-time
     */
    validateTickerInput() {
        const ticker = this.tickerInput.value.trim().toUpperCase();
        
        this.clearMessages();
        
        if (!ticker) {
            this.feedbackEl.textContent = '';
            return true;
        }
        
        const isValid = /^[A-Z]{1,6}$/.test(ticker);
        
        if (!isValid) {
            if (ticker.length > 6) {
                this.feedbackEl.textContent = 'Ticker must be 6 characters or less';
                this.feedbackEl.style.color = '#e74c3c';
            } else if (/[^A-Z]/.test(ticker)) {
                this.feedbackEl.textContent = 'Ticker must contain only letters (A-Z)';
                this.feedbackEl.style.color = '#e74c3c';
            }
            return false;
        } else {
            this.feedbackEl.textContent = '✓ Valid ticker format';
            this.feedbackEl.style.color = '#27ae60';
            return true;
        }
    }
    
    /**
     * Handle form submission
     * @param {Event} e - Form submit event
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const ticker = this.tickerInput.value.trim().toUpperCase();
        
        if (!this.validateTickerInput()) {
            this.showError('Please enter a valid ticker symbol (1-6 letters only)');
            return;
        }
        
        if (!ticker) {
            this.showError('Please enter a stock ticker symbol');
            return;
        }
        
        await this.submitTicker(ticker);
    }
    
    /**
     * Submit ticker to backend for validation and session initialization
     * @param {string} ticker - Stock ticker symbol
     */
    async submitTicker(ticker) {
        this.clearMessages();
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Validating...';
        
        try {
            const response = await fetch('/api/assessment/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker_symbol: ticker })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.handleSuccessfulValidation(data);
            } else {
                this.showError(data.detail || 'Invalid ticker symbol');
            }
        } catch (error) {
            console.error('Error submitting ticker:', error);
            this.showError('Unable to connect to server. Please try again.');
        } finally {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.textContent = 'Analyze Stock';
        }
    }
    
    /**
     * Handle successful ticker validation
     * @param {object} data - Response data from server
     */
    handleSuccessfulValidation(data) {
        this.clearMessages();
        this.resultsContainer.innerHTML = `
            <div class="success-message" style="color: #27ae60; padding: 1rem; background: #d5f4e6; border-radius: 4px; border-left: 4px solid #27ae60;">
                <h3>Session Initialized</h3>
                <p><strong>Ticker:</strong> ${data.ticker_symbol}</p>
                <p><strong>Session ID:</strong> ${data.session_id}</p>
                <p><strong>Status:</strong> ${data.status}</p>
                <p style="margin-top: 1rem;">Assessment functionality will be implemented in the next story.</p>
            </div>
        `;
        
        sessionStorage.setItem('currentSession', JSON.stringify({
            sessionId: data.session_id,
            tickerSymbol: data.ticker_symbol,
            currentStep: 'ticker',
            status: data.status
        }));
    }
    
    /**
     * Display error message to user
     * @param {string} message - Error message to display
     */
    showError(message) {
        this.errorEl.textContent = message;
        this.errorEl.style.display = 'block';
        this.feedbackEl.textContent = '';
    }
    
    /**
     * Clear all messages
     */
    clearMessages() {
        this.errorEl.textContent = '';
        this.errorEl.style.display = 'none';
        this.feedbackEl.textContent = '';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockIQApp();
});