# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: StockIQ Collaborative Research API
  version: 2.0.0
  description: Multi-agent collaborative investment research API with shared knowledge base
servers:
  - url: http://localhost:8000
    description: Local development server

paths:
  /health:
    get:
      summary: Health check endpoint
      responses:
        '200':
          description: Service is healthy

  /api/assessment/start:
    post:
      summary: Initialize assessment session
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                ticker_symbol:
                  type: string
                  example: "ASML"
      responses:
        '200':
          description: Assessment session created

  /api/research/start:
    post:
      summary: Begin collaborative research process
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                session_id:
                  type: string
                research_depth:
                  type: string
                  enum: ['comprehensive', 'executive']
      responses:
        '202':
          description: Research started

  /api/research/database:
    get:
      summary: Get current research database contents
      parameters:
        - name: session_id
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Research database contents
          content:
            application/json:
              schema:
                type: object
                properties:
                  files:
                    type: array
                    items:
                      $ref: '#/components/schemas/ResearchFile'

  /api/reports/generate:
    post:
      summary: Generate final report using chunked generation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                session_id:
                  type: string
                expertise_level:
                  type: integer
      responses:
        '202':
          description: Report generation started

  /api/reports/status:
    get:
      summary: Check report generation progress
      parameters:
        - name: session_id
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Generation status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenerationStatus'

components:
  schemas:
    ResearchFile:
      type: object
      properties:
        file_path:
          type: string
        author_agent:
          type: string
        created_at:
          type: string
          format: date-time
        version:
          type: integer
        topic:
          type: string
        cross_references:
          type: array
          items:
            type: string

    GenerationStatus:
      type: object
      properties:
        session_id:
          type: string
        current_section:
          type: string
        progress:
          type: number
        status:
          type: string
          enum: ['generating', 'merging', 'converting', 'complete', 'error']
        sections_complete:
          type: integer
        total_sections:
          type: integer
```
