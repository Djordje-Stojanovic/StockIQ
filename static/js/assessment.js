/**
 * StockIQ Assessment Frontend Module
 * Handles 20-question contextual assessment interface with progressive presentation
 */

class AssessmentManager {
    constructor() {
        this.questions = [];
        this.responses = [];
        this.currentQuestionIndex = 0;
        this.sessionData = null;
        this.assessmentContainer = null;
        this.startTime = null;
        this.questionStartTime = null;
        
        this.init();
    }
    
    /**
     * Initialize assessment module
     */
    init() {
        this.createAssessmentContainer();
        this.loadSessionData();
    }
    
    /**
     * Create assessment container in DOM
     */
    createAssessmentContainer() {
        const container = document.createElement('div');
        container.id = 'assessment-container';
        container.className = 'assessment-container';
        container.style.display = 'none';
        
        container.innerHTML = `
            <div class="assessment-header">
                <h2>Investment Expertise Assessment</h2>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="assessment-progress"></div>
                    </div>
                    <div class="progress-text" id="progress-text">Question 1 of 20</div>
                </div>
            </div>
            
            <div class="question-container">
                <div class="question-content" id="question-content">
                    <div class="question-text" id="question-text"></div>
                    <div class="question-options" id="question-options"></div>
                </div>
                
                <div class="question-navigation">
                    <button id="prev-btn" class="nav-btn" disabled>Previous</button>
                    <button id="next-btn" class="nav-btn" disabled>Next</button>
                    <button id="submit-assessment-btn" class="submit-btn" style="display: none;">Submit Assessment</button>
                </div>
            </div>
            
            <div class="assessment-results" id="assessment-results" style="display: none;">
                <h3>Assessment Complete!</h3>
                <div id="results-content"></div>
            </div>
        `;
        
        document.querySelector('main').appendChild(container);
        this.assessmentContainer = container;
        this.setupEventListeners();
    }
    
    /**
     * Load session data from sessionStorage
     */
    loadSessionData() {
        const stored = sessionStorage.getItem('currentSession');
        if (stored) {
            this.sessionData = JSON.parse(stored);
        }
    }
    
    /**
     * Setup event listeners for assessment interface
     */
    setupEventListeners() {
        document.getElementById('prev-btn').addEventListener('click', () => this.previousQuestion());
        document.getElementById('next-btn').addEventListener('click', () => this.nextQuestion());
        document.getElementById('submit-assessment-btn').addEventListener('click', () => this.submitAssessment());
    }
    
    /**
     * Start the assessment process
     * @param {string} sessionId - Session identifier
     * @param {string} ticker - Stock ticker symbol
     */
    async startAssessment(sessionId, ticker) {
        this.sessionData = { sessionId, tickerSymbol: ticker };
        
        try {
            // Show loading state
            this.showLoading('Generating personalized assessment questions...');
            
            // Fetch questions from backend
            console.log('🚀 API REQUEST: Getting assessment questions', {
                endpoint: `/api/assessment/questions?session_id=${sessionId}`,
                method: 'GET',
                sessionId: sessionId,
                ticker: ticker
            });
            
            const response = await fetch(`/api/assessment/questions?session_id=${sessionId}`);
            const data = await response.json();
            
            console.log('✅ API RESPONSE: Assessment questions received', {
                status: response.status,
                questionCount: data.questions?.length || 0,
                data: data
            });
            
            if (response.ok) {
                this.questions = data.questions;
                this.responses = new Array(this.questions.length).fill(null);
                this.currentQuestionIndex = 0;
                this.startTime = Date.now();
                
                this.showAssessment();
                this.displayCurrentQuestion();
            } else {
                this.showError(data.detail || 'Failed to load assessment questions');
            }
        } catch (error) {
            console.error('Error starting assessment:', error);
            this.showError('Unable to connect to server. Please try again.');
        }
    }
    
    /**
     * Show loading state
     * @param {string} message - Loading message
     */
    showLoading(message) {
        this.assessmentContainer.style.display = 'block';
        this.assessmentContainer.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.assessmentContainer.style.display = 'block';
        this.assessmentContainer.innerHTML = `
            <div class="error-container">
                <h3>Assessment Error</h3>
                <p>${message}</p>
                <button onclick="this.parentElement.parentElement.style.display='none'">Close</button>
            </div>
        `;
    }
    
    /**
     * Show assessment interface
     */
    showAssessment() {
        // Hide other sections
        document.querySelector('.input-section').style.display = 'none';
        document.querySelector('.results-section').style.display = 'none';
        
        // Hide any existing assessment containers
        const existingContainers = document.querySelectorAll('#assessment-container');
        existingContainers.forEach(container => container.remove());
        
        // Recreate clean interface
        this.createAssessmentContainer();
        this.assessmentContainer.style.display = 'block';
    }
    
    /**
     * Display current question
     */
    displayCurrentQuestion() {
        if (!this.questions || this.currentQuestionIndex >= this.questions.length) return;
        
        const question = this.questions[this.currentQuestionIndex];
        this.questionStartTime = Date.now();
        
        // Update progress
        this.updateProgress();
        
        // Display question
        document.getElementById('question-text').textContent = question.question;
        
        // Display options
        const optionsContainer = document.getElementById('question-options');
        optionsContainer.innerHTML = '';
        
        question.options.forEach((option, index) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'option-item';
            
            const isSelected = this.responses[this.currentQuestionIndex]?.selected_option === index;
            
            optionDiv.innerHTML = `
                <input type="radio" 
                       id="option-${index}" 
                       name="question-${this.currentQuestionIndex}" 
                       value="${index}"
                       ${isSelected ? 'checked' : ''}>
                <label for="option-${index}">${option}</label>
            `;
            
            optionDiv.addEventListener('click', () => this.selectOption(index));
            optionsContainer.appendChild(optionDiv);
        });
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    /**
     * Update progress indicator
     */
    updateProgress() {
        const progress = ((this.currentQuestionIndex + 1) / this.questions.length) * 100;
        document.getElementById('assessment-progress').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = 
            `Question ${this.currentQuestionIndex + 1} of ${this.questions.length}`;
    }
    
    /**
     * Select an option for current question
     * @param {number} optionIndex - Selected option index
     */
    selectOption(optionIndex) {
        const question = this.questions[this.currentQuestionIndex];
        const timeTaken = (Date.now() - this.questionStartTime) / 1000;
        
        // Update radio button
        document.getElementById(`option-${optionIndex}`).checked = true;
        
        // Store response
        this.responses[this.currentQuestionIndex] = {
            question_id: this.currentQuestionIndex + 1,
            selected_option: optionIndex,
            correct_option: question.correct_answer_index,
            time_taken: timeTaken,
            partial_credit: 0.0
        };
        
        // Enable next button
        document.getElementById('next-btn').disabled = false;
        
        // Show submit button if last question
        if (this.currentQuestionIndex === this.questions.length - 1) {
            document.getElementById('submit-assessment-btn').style.display = 'inline-block';
        }
    }
    
    /**
     * Navigate to previous question
     */
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }
    
    /**
     * Navigate to next question
     */
    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayCurrentQuestion();
        }
    }
    
    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const submitBtn = document.getElementById('submit-assessment-btn');
        
        // Previous button
        prevBtn.disabled = this.currentQuestionIndex === 0;
        
        // Next button
        const hasResponse = this.responses[this.currentQuestionIndex] !== null;
        const isLastQuestion = this.currentQuestionIndex === this.questions.length - 1;
        
        nextBtn.disabled = !hasResponse || isLastQuestion;
        nextBtn.style.display = isLastQuestion ? 'none' : 'inline-block';
        
        // Submit button
        submitBtn.style.display = (isLastQuestion && hasResponse) ? 'inline-block' : 'none';
    }
    
    /**
     * Submit completed assessment
     */
    async submitAssessment() {
        if (!this.allQuestionsAnswered()) {
            alert('Please answer all questions before submitting.');
            return;
        }
        
        try {
            // Show loading
            document.getElementById('submit-assessment-btn').textContent = 'Submitting...';
            document.getElementById('submit-assessment-btn').disabled = true;
            
            const requestBody = {
                session_id: this.sessionData.sessionId,
                responses: this.responses.filter(r => r !== null)
            };
            
            console.log('🚀 API REQUEST: Submitting assessment', {
                endpoint: '/api/assessment/submit',
                method: 'POST',
                requestBody: requestBody
            });
            
            const response = await fetch('/api/assessment/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            
            console.log('✅ API RESPONSE: Assessment submitted', {
                status: response.status,
                data: data
            });
            
            if (response.ok) {
                // Extract result from API response structure
                const resultData = data.result || data;
                this.displayResults(resultData);
            } else {
                this.showError(data.detail || 'Failed to submit assessment');
            }
        } catch (error) {
            console.error('Error submitting assessment:', error);
            this.showError('Unable to connect to server. Please try again.');
        }
    }
    
    /**
     * Check if all questions have been answered
     * @returns {boolean} True if all questions answered
     */
    allQuestionsAnswered() {
        return this.responses.every(response => response !== null);
    }
    
    /**
     * Display assessment results
     * @param {object} results - Assessment results from backend
     */
    displayResults(results) {
        document.querySelector('.question-container').style.display = 'none';
        document.getElementById('assessment-results').style.display = 'block';
        
        const resultsContent = document.getElementById('results-content');
        resultsContent.innerHTML = `
            <div class="expertise-level">
                <h4>Your Expertise Level: ${results.expertise_level}/10</h4>
                <div class="level-bar">
                    <div class="level-fill" style="width: ${(results.expertise_level / 10) * 100}%"></div>
                </div>
            </div>
            
            <div class="report-complexity">
                <p><strong>Recommended Report Type:</strong> 
                   ${results.report_complexity === 'comprehensive' ? 
                     'Comprehensive (200-300 pages)' : 
                     'Executive Summary (10-20 pages)'}</p>
            </div>
            
            <div class="explanation">
                <h4>Assessment Explanation:</h4>
                <p>${results.explanation}</p>
            </div>
            
            <div class="next-steps">
                <button id="continue-to-analysis" class="primary-btn">Continue to Stock Analysis</button>
                <button id="retake-assessment" class="secondary-btn">Retake Assessment</button>
            </div>
        `;
        
        // Update session data
        this.sessionData.expertiseLevel = results.expertise_level;
        this.sessionData.reportComplexity = results.report_complexity;
        this.sessionData.currentStep = 'assessment_complete';
        sessionStorage.setItem('currentSession', JSON.stringify(this.sessionData));
        
        // Setup next steps
        document.getElementById('continue-to-analysis').addEventListener('click', () => {
            this.continueToAnalysis();
        });
        
        document.getElementById('retake-assessment').addEventListener('click', () => {
            this.retakeAssessment();
        });
    }
    
    /**
     * Continue to stock analysis phase
     */
    continueToAnalysis() {
        this.assessmentContainer.style.display = 'none';
        document.querySelector('.results-section').style.display = 'block';
        
        document.getElementById('results-container').innerHTML = `
            <div class="analysis-ready">
                <h3>Ready for Analysis</h3>
                <p><strong>Ticker:</strong> ${this.sessionData.tickerSymbol}</p>
                <p><strong>Expertise Level:</strong> ${this.sessionData.expertiseLevel}/10</p>
                <p><strong>Report Type:</strong> ${this.sessionData.reportComplexity}</p>
                <p style="margin-top: 1rem;">Multi-agent analysis will be implemented in future stories.</p>
            </div>
        `;
    }
    
    /**
     * Restart the assessment
     */
    retakeAssessment() {
        this.responses = new Array(this.questions.length).fill(null);
        this.currentQuestionIndex = 0;
        this.startTime = Date.now();
        
        document.getElementById('assessment-results').style.display = 'none';
        document.querySelector('.question-container').style.display = 'block';
        
        this.displayCurrentQuestion();
    }
    
    /**
     * Hide assessment and return to main interface
     */
    hideAssessment() {
        this.assessmentContainer.style.display = 'none';
        document.querySelector('.input-section').style.display = 'block';
        document.querySelector('.results-section').style.display = 'block';
    }
}

// Export for use by main application
window.AssessmentManager = AssessmentManager;