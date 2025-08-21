/**
 * StockIQ Main Frontend Application
 * Handles health check, ticker input, and basic API communication
 */

class StockIQApp {
    constructor() {
        this.healthStatusEl = document.getElementById('health-status');
        this.tickerInput = document.getElementById('ticker');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.resultsContainer = document.getElementById('results-container');
        
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
        this.analyzeBtn.addEventListener('click', () => this.analyzeStock());
        this.tickerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeStock();
            }
        });
    }
    
    /**
     * Analyze stock ticker (placeholder for future implementation)
     */
    analyzeStock() {
        const ticker = this.tickerInput.value.trim().toUpperCase();
        
        if (!ticker) {
            this.showError('Please enter a stock ticker symbol');
            return;
        }
        
        // Placeholder implementation - to be expanded in future stories
        this.resultsContainer.innerHTML = `
            <div class="analysis-placeholder">
                <h3>Analysis for ${ticker}</h3>
                <p>Stock analysis functionality will be implemented in upcoming stories.</p>
                <p>This foundation provides:</p>
                <ul>
                    <li>FastAPI backend with health monitoring</li>
                    <li>Complete project structure for agents and services</li>
                    <li>Environment configuration management</li>
                    <li>Frontend interface for user interaction</li>
                </ul>
            </div>
        `;
    }
    
    /**
     * Display error message to user
     * @param {string} message - Error message to display
     */
    showError(message) {
        this.resultsContainer.innerHTML = `
            <div class="error-message" style="color: #e74c3c; padding: 1rem; background: #fdf2f2; border-radius: 4px;">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockIQApp();
});