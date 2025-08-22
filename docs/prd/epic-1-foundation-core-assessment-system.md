# Epic 1: Foundation & Core Assessment System

**Epic Goal:** Establish complete project foundation with FastAPI infrastructure, implement AI-powered contextual assessment system, and deliver working ticker input with accurate expertise level calculation (1-10 scale). Users can input any company ticker, complete dynamically generated ticker-specific assessment, and receive their expertise score with system validation.

## Story 1.1: Project Setup & FastAPI Foundation
As a developer,
I want a complete FastAPI project structure with essential configuration,
so that I have a solid foundation for implementing the assessment and research agents.

### Acceptance Criteria
1. FastAPI application initializes with health check endpoint
2. Project structure includes agents/, api/, templates/, static/ directories
3. Environment configuration supports OpenAI API key management
4. Basic CORS and middleware configuration for local development
5. Requirements.txt includes minimal dependencies (FastAPI, OpenAI SDK, Pydantic, weasyprint)
6. Application runs locally on Windows 11 with simple startup command

## Story 1.2: Ticker Input & Validation System
As a user,
I want to enter any company ticker symbol through a clean web interface,
so that I can initiate research analysis for my chosen company.

### Acceptance Criteria
1. Simple HTML form accepts ticker symbol input (e.g., ASML, COST, MSFT)
2. Client-side validation ensures ticker format is appropriate (letters, limited length)
3. FastAPI endpoint validates ticker and returns confirmation or error
4. Basic ticker existence validation (simple format checking for MVP)
5. Error handling for invalid tickers with clear user feedback
6. Session initialization to maintain context throughout assessment process

## Story 1.3: Assessment Agent Implementation
As a user,
I want to complete a sophisticated 20-question assessment of my financial expertise,
so that the system can adapt its analysis depth to my knowledge level.

### Acceptance Criteria
1. Assessment agent dynamically generates exactly 20 contextual questions (2 per difficulty level 1-10) tailored to the specific ticker and covering general investing knowledge, ticker-specific understanding, sector expertise, and analytical sophistication
2. Questions are presented one at a time with clear progress indication (Question 5 of 20)
3. Answer scoring system calculates expertise level on 1-10 scale with transparent logic based on contextual question difficulty
4. Question difficulty progresses from basic concepts (Level 1: knows S&P 500 exists) to expert analysis (Level 10: top-tier analyst knowledge of specific company)
5. User can navigate back to previous questions during assessment
6. Assessment completion triggers expertise level calculation and display
7. Assessment results are saved to session context for downstream agents

## Story 1.4: Assessment Scoring & Level Determination
As a user,
I want to receive an accurate expertise level score (1-10) based on my assessment responses,
so that subsequent research analysis is appropriately calibrated to my knowledge.

### Acceptance Criteria
1. Scoring algorithm weights questions by difficulty and domain expertise
2. Final expertise level (1-10) is calculated with clear explanation of scoring rationale
3. Score determines analysis depth: levels 1-5 trigger comprehensive reports, 6-10 trigger expert summaries
4. User receives immediate feedback on their expertise level and what it means for their report
5. Scoring results are preserved for downstream research agent coordination
6. System provides option to retake assessment if user disagrees with results

## Story 1.5: Session Management & Context Preservation
As a user,
I want my ticker selection and assessment results to be maintained throughout the process,
so that I can seamlessly progress from assessment to research without losing context.

### Acceptance Criteria
1. Session storage maintains ticker symbol, assessment responses, and expertise level
2. User can see current session status (ticker, expertise level) on all pages
3. Session expires after reasonable timeout with clear user notification
4. Context data is formatted for easy handoff to research agents
5. Error recovery allows users to resume from where they left off if issues occur
6. Session clear functionality allows users to start fresh analysis
