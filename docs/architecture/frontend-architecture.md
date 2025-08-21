# Frontend Architecture

## Component Architecture

### Component Organization
```
static/
├── css/
│   ├── styles.css              # Institutional styling
│   └── assessment.css          # Assessment-specific styles
├── js/
│   ├── app.js                  # Main application logic  
│   ├── assessment.js           # Assessment workflow
│   ├── research_monitor.js     # Real-time research progress
│   └── utils.js                # Utility functions
└── index.html                  # Single page application
```

### Component Template
```typescript
// Enhanced component for research monitoring
class ResearchMonitorComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.sessionId = null;
        this.pollInterval = null;
        this.init();
    }

    init() {
        this.render();
        this.bindEvents();
    }

    render() {
        this.container.innerHTML = `
            <div class="research-progress">
                <h3>Research in Progress</h3>
                <div id="agent-status">
                    <div class="agent-card" data-agent="valuation">
                        <h4>Valuation Expert</h4>
                        <div class="status">Idle</div>
                        <div class="files-contributed">0 files</div>
                    </div>
                    <div class="agent-card" data-agent="strategic">
                        <h4>Strategic Analyst</h4>
                        <div class="status">Idle</div>
                        <div class="files-contributed">0 files</div>
                    </div>
                    <div class="agent-card" data-agent="historian">
                        <h4>Company Historian</h4>
                        <div class="status">Idle</div>
                        <div class="files-contributed">0 files</div>
                    </div>
                </div>
                <div id="research-database">
                    <h4>Research Database</h4>
                    <div id="file-list"></div>
                </div>
            </div>
        `;
    }

    startMonitoring(sessionId) {
        this.sessionId = sessionId;
        this.pollInterval = setInterval(() => {
            this.updateStatus();
        }, 2000); // Poll every 2 seconds
    }

    async updateStatus() {
        try {
            const response = await fetch(`/api/research/status?session_id=${this.sessionId}`);
            const status = await response.json();
            this.updateAgentStatus(status.agents);
            this.updateResearchDatabase(status.research_files);
        } catch (error) {
            console.error('Failed to update research status:', error);
        }
    }

    updateAgentStatus(agents) {
        Object.entries(agents).forEach(([agentName, agentStatus]) => {
            const agentCard = this.container.querySelector(`[data-agent="${agentName}"]`);
            if (agentCard) {
                agentCard.querySelector('.status').textContent = agentStatus.status;
                agentCard.querySelector('.files-contributed').textContent = 
                    `${agentStatus.files_contributed} files`;
                agentCard.className = `agent-card ${agentStatus.status}`;
            }
        });
    }

    updateResearchDatabase(files) {
        const fileList = this.container.querySelector('#file-list');
        fileList.innerHTML = files.map(file => `
            <div class="research-file">
                <span class="file-name">${file.name}</span>
                <span class="file-author">by ${file.author}</span>
                <span class="file-time">${file.created_at}</span>
            </div>
        `).join('');
    }

    stopMonitoring() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
}
```

## State Management Architecture

### State Structure
```typescript
// Enhanced state management for collaborative research
interface AppState {
    currentSession: {
        sessionId: string;
        tickerSymbol: string;
        currentStep: 'ticker' | 'assessment' | 'research' | 'generation' | 'complete';
        expertiseLevel?: number;
        reportComplexity?: 'comprehensive' | 'executive';
    };
    assessment: {
        currentQuestion: number;
        responses: AssessmentResponse[];
        totalQuestions: number;
    };
    research: {
        activeAgents: string[];
        completedAgents: string[];
        researchDatabase: {
            files: ResearchFile[];
            totalFiles: number;
            lastUpdate: string;
        };
        collaborationActivity: {
            comments: number;
            crossReferences: number;
        };
    };
    reportGeneration: {
        status: 'pending' | 'generating' | 'merging' | 'converting' | 'complete' | 'error';
        currentSection: string;
        sectionsComplete: number;
        totalSections: number;
        estimatedTimeRemaining: number;
    };
}
```

## Frontend Services Layer

### API Client Setup
```typescript
class StockIQApiClient {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
    }

    async startResearch(sessionId, researchDepth) {
        const response = await fetch(`${this.baseURL}/research/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                research_depth: researchDepth
            })
        });
        return response.json();
    }

    async getResearchStatus(sessionId) {
        const response = await fetch(`${this.baseURL}/research/status?session_id=${sessionId}`);
        return response.json();
    }

    async getResearchDatabase(sessionId) {
        const response = await fetch(`${this.baseURL}/research/database?session_id=${sessionId}`);
        return response.json();
    }

    async generateReport(sessionId, expertiseLevel) {
        const response = await fetch(`${this.baseURL}/reports/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                expertise_level: expertiseLevel
            })
        });
        return response.json();
    }

    async getReportStatus(sessionId) {
        const response = await fetch(`${this.baseURL}/reports/status?session_id=${sessionId}`);
        return response.json();
    }
}
```
