# Chunked Report Generation Architecture

## Dynamic Scaling Report Generator

```python
class ChunkedReportGenerator:
    def __init__(self, session_id: str, expertise_level: int):
        self.session_id = session_id
        self.expertise_level = expertise_level
        self.research_db = ResearchDatabaseManager()
        self.context_manager = ContextManager()
        self.openai_client = OpenAIClient()
        
    async def generate_adaptive_report(self) -> str:
        """Generate report with dynamic scaling based on expertise level"""
        
        # Determine report structure based on expertise
        sections = self.determine_report_sections(self.expertise_level)
        
        # Read complete research database
        research_context = await self.research_db.read_all_research(self.session_id)
        
        # Generate sections with rolling context
        generated_sections = []
        cumulative_content = ""
        
        for section_spec in sections:
            # Prepare context with previous sections + research database
            section_context = self.prepare_section_context(
                research_context,
                cumulative_content,
                section_spec
            )
            
            # Generate section
            section_content = await self.generate_section(section_spec, section_context)
            generated_sections.append(section_content)
            
            # Update cumulative context for next section
            cumulative_content += f"\n\n## {section_spec.title}\n\n{section_content}"
            
            # Manage context size
            cumulative_content = self.context_manager.trim_context(
                cumulative_content, max_tokens=150000
            )
        
        # Merge all sections
        final_report = self.merge_sections(generated_sections, self.expertise_level)
        
        # Save complete report to research database
        await self.research_db.write_research(
            agent_name="synthesis",
            session_id=self.session_id,
            topic="final_report",
            content=final_report,
            metadata={
                "expertise_level": self.expertise_level,
                "total_sections": len(sections),
                "word_count": len(final_report.split()),
                "generation_method": "chunked_adaptive"
            }
        )
        
        return final_report
    
    def determine_report_sections(self, expertise_level: int) -> List[SectionSpec]:
        """Dynamically determine report sections based on expertise level"""
        
        # Base sections for all reports
        base_sections = [
            SectionSpec("executive_summary", "Executive Summary", priority=1),
            SectionSpec("investment_thesis", "Investment Thesis", priority=1),
            SectionSpec("valuation_analysis", "Valuation Analysis", priority=1),
            SectionSpec("strategic_assessment", "Strategic Assessment", priority=1),
            SectionSpec("risks_and_opportunities", "Risks and Opportunities", priority=1),
            SectionSpec("recommendation", "Investment Recommendation", priority=1)
        ]
        
        # Expertise-based scaling
        if expertise_level <= 5:  # Comprehensive report
            comprehensive_sections = [
                SectionSpec("company_overview", "Company Overview and History", priority=2),
                SectionSpec("industry_analysis", "Industry Dynamics and Context", priority=2),
                SectionSpec("financial_deep_dive", "Financial Analysis Deep Dive", priority=2),
                SectionSpec("competitive_positioning", "Competitive Positioning Analysis", priority=2),
                SectionSpec("management_assessment", "Management and Leadership Assessment", priority=2),
                SectionSpec("esg_considerations", "ESG and Sustainability Factors", priority=3),
                SectionSpec("scenario_analysis", "Scenario and Sensitivity Analysis", priority=3),
                SectionSpec("peer_comparison_detailed", "Detailed Peer Comparison", priority=3),
                SectionSpec("appendices", "Appendices and Supporting Data", priority=3)
            ]
            all_sections = base_sections + comprehensive_sections
            
            # Scale depth based on specific expertise level
            for section in all_sections:
                if expertise_level <= 3:
                    section.depth_multiplier = 2.5  # Very detailed explanations
                    section.include_educational_content = True
                elif expertise_level <= 5:
                    section.depth_multiplier = 1.8  # Moderately detailed
                    section.include_educational_content = True
            
        else:  # Executive summary format (6-10)
            # More focused, higher-level sections
            for section in base_sections:
                section.depth_multiplier = 0.7  # Condensed format
                section.include_educational_content = False
                section.focus_on_key_insights = True
            
            all_sections = base_sections
        
        return sorted(all_sections, key=lambda x: x.priority)
    
    async def generate_section(self, section_spec: SectionSpec, context: str) -> str:
        """Generate individual section with adaptive scaling"""
        
        # Determine target length based on expertise level and section
        if self.expertise_level <= 5:
            target_tokens = section_spec.priority * 2000 * section_spec.depth_multiplier
        else:
            target_tokens = section_spec.priority * 800 * section_spec.depth_multiplier
        
        section_prompt = f"""
        You are generating the "{section_spec.title}" section of an institutional investment research report.
        
        User expertise level: {self.expertise_level}/10
        Target depth: {"Comprehensive educational" if self.expertise_level <= 5 else "Executive focused"}
        Target length: {int(target_tokens)} tokens approximately
        
        Research context and previous sections:
        {context[-100000:]}  # Use last 100k tokens of context
        
        Generate this section following these guidelines:
        - {"Include educational explanations of financial concepts" if section_spec.include_educational_content else "Focus on key insights for experienced investors"}
        - {"Provide detailed analysis with supporting data" if section_spec.depth_multiplier > 1 else "Provide concise, high-level analysis"}
        - Maintain institutional research quality and professional tone
        - Cross-reference insights from other sections where relevant
        - Use markdown formatting with appropriate headers and structure
        
        Section focus: {section_spec.title}
        """
        
        section_content = await self.openai_client.analysis_call(
            prompt=section_prompt,
            max_tokens=min(int(target_tokens * 1.2), 8000),  # Allow some overage
            temperature=0.4
        )
        
        return section_content
    
    def prepare_section_context(self, research_db_content: str, previous_sections: str, section_spec: SectionSpec) -> str:
        """Prepare optimized context for section generation"""
        
        # Prioritize research database content relevant to this section
        relevant_research = self.extract_relevant_research(research_db_content, section_spec.title)
        
        # Combine with previous sections (truncated if necessary)
        context = f"""
        # Research Database Content (Relevant to {section_spec.title})
        {relevant_research[:60000]}
        
        # Previous Report Sections
        {previous_sections[-80000:]}
        
        # Section to Generate: {section_spec.title}
        Priority: {section_spec.priority}
        Depth Multiplier: {section_spec.depth_multiplier}
        """
        
        return context
    
    def extract_relevant_research(self, research_content: str, section_title: str) -> str:
        """Extract research most relevant to current section"""
        # Simple relevance extraction - could be enhanced with embeddings
        relevance_keywords = {
            "executive_summary": ["summary", "key findings", "recommendation", "thesis"],
            "valuation_analysis": ["owner-returns", "fcf-share", "price-ladder", "irr-decomposition", "valuation", "price target", "financial metrics"],
            "strategic_assessment": ["competitive", "strategy", "market position", "moat"],
            "company_overview": ["history", "timeline", "leadership", "business model"],
            # Add more mappings as needed
        }
        
        keywords = relevance_keywords.get(section_title.lower().replace(" ", "_"), [])
        
        if not keywords:
            return research_content  # Return full context if no specific keywords
        
        # Simple keyword-based extraction
        relevant_parts = []
        for line in research_content.split('\n'):
            if any(keyword.lower() in line.lower() for keyword in keywords):
                relevant_parts.append(line)
        
        return '\n'.join(relevant_parts) if relevant_parts else research_content
```
