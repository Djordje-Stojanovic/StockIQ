"""Data models for Owner-Returns FCF/Share analysis framework."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class IRRComponents(BaseModel):
    """
    IRR decomposition components per elite investor framework.
    
    IRR = Starting Yield + FCF/share Growth + Multiple Reversion - Dilution ± Leverage
    """

    ticker: str = Field(default="", description="Company ticker symbol")
    total_irr: float = Field(default=0.08, ge=-1.0, le=2.0, description="Total IRR calculation")
    starting_yield: float = Field(default=0.08, ge=0.0, le=1.0, description="FCF per share / Current price")
    fcf_growth_component: float = Field(default=0.10, ge=-0.5, le=1.0, description="Annual FCF/share compound growth")
    multiple_reversion_component: float = Field(default=0.0, ge=-0.5, le=0.5, description="Annual multiple expansion/contraction")
    dilution_drag: float = Field(default=-0.015, ge=-0.1, le=0.0, description="Share dilution impact (negative)")
    leverage_effect: float = Field(default=0.0, ge=-0.1, le=0.1, description="Leverage impact on per-share returns")
    dividend_yield: float = Field(default=0.0, ge=0.0, le=0.2, description="Current dividend yield")
    breakdown_explanation: str = Field(default="IRR analysis in markdown file", description="Explanation of IRR calculation")

    def calculate_total_irr(self) -> float:
        """Calculate total IRR from components."""
        return (self.starting_yield + self.fcf_growth_component + self.multiple_reversion_component +
                self.dilution_drag + self.leverage_effect + self.dividend_yield)


class FCFProjections(BaseModel):
    """Free Cash Flow per share projections over 10-year horizon."""

    ticker: str = Field(default="", description="Company ticker symbol")
    base_fcf_per_share: float = Field(default=12.0, gt=0.0, description="Current FCF per share (LTM)")
    historical_fcf_per_share: list[float] = Field(default_factory=lambda: [8.0, 9.5, 11.0, 11.5, 12.0], description="Historical FCF per share data")
    projection_years: int = Field(default=10, ge=5, le=15, description="Projection horizon")
    annual_fcf_per_share: list[float] = Field(default_factory=lambda: [13.2, 14.5, 16.0, 17.6, 19.4, 21.3, 23.4, 25.8, 28.4, 31.2], description="Annual FCF/share projections")
    growth_rates: list[float] = Field(default_factory=lambda: [0.10] * 10, description="Annual growth rates used")
    fade_assumptions: dict[str, Any] = Field(default_factory=lambda: {"logic": "Conservative fade to industry median ROIC by year 10"}, description="Base-rate fade logic applied")
    dilution_rate: float = Field(default=0.015, ge=0.0, le=0.1, description="Annual share dilution rate")

    @field_validator('annual_fcf_per_share')
    @classmethod
    def validate_projections_length(cls, v, info):
        """Ensure projections match projection years (relaxed for MVP)."""
        # MVP: Just ensure we have some projections
        if len(v) < 5:
            # Pad with defaults if needed
            return v + [v[-1] * 1.1] * (10 - len(v)) if v else [12.0] * 10
        return v[:15]  # Cap at max 15

    @field_validator('growth_rates')
    @classmethod  
    def validate_growth_rates_length(cls, v, info):
        """Ensure growth rates match projection years (relaxed for MVP)."""
        # MVP: Just ensure we have some growth rates
        if len(v) < 5:
            # Pad with defaults if needed
            return v + [0.10] * (10 - len(v)) if v else [0.10] * 10
        return v[:15]  # Cap at max 15

    def get_final_year_fcf(self) -> float:
        """Get FCF per share in final projection year."""
        return self.annual_fcf_per_share[-1] if self.annual_fcf_per_share else 0.0

    def get_compound_growth_rate(self) -> float:
        """Calculate compound annual growth rate over projection period."""
        if not self.annual_fcf_per_share or self.base_fcf_per_share <= 0:
            return 0.0

        final_fcf = self.get_final_year_fcf()
        years = len(self.annual_fcf_per_share)
        return (final_fcf / self.base_fcf_per_share) ** (1/years) - 1


class PriceLadderBand(BaseModel):
    """Individual price band in the Price Ladder framework."""

    band_name: str = Field(default="", description="Band identifier (buffett_floor, min_irr_10pct, target_irr_15pct)")
    price_threshold: float = Field(default=120.0, gt=0.0, description="Price threshold for this band")
    discount_to_current: float = Field(default=-0.20, description="Discount/premium to current price")
    irr_threshold: float | None = Field(default=None, description="IRR threshold for this band")
    description: str = Field(default="Price ladder analysis", description="Human-readable band description")
    action_recommendation: str = Field(default="BUY", description="Investment action for this band")
    must_be_true_kpis: list[str] = Field(default_factory=list, description="Must-be-true KPIs for this band")

    @field_validator('discount_to_current')
    @classmethod
    def validate_discount_range(cls, v):
        """Ensure discount is within reasonable range."""
        if v < -2.0 or v > 2.0:  # -200% to +200%
            raise ValueError("Discount to current price outside reasonable range")
        return v


class PriceLadderAnalysis(BaseModel):
    """Complete Price Ladder analysis per elite investor practices."""

    ticker: str = Field(default="", description="Company ticker symbol")
    current_price: float = Field(default=150.0, gt=0.0, description="Current stock price")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    # Price bands (optional for MVP)
    buffett_floor_band: PriceLadderBand = Field(default_factory=PriceLadderBand, description="Buffett Floor (10x pre-tax earnings)")
    min_irr_band: PriceLadderBand = Field(default_factory=PriceLadderBand, description="Minimum 10% IRR threshold")
    target_irr_band: PriceLadderBand = Field(default_factory=PriceLadderBand, description="Target 15% IRR threshold")

    # Overall assessment
    overall_recommendation: str = Field(default="HOLD", description="Overall investment recommendation")
    recommendation_rationale: str = Field(default="Analysis in markdown file", description="Rationale for recommendation")
    position_sizing_guidance: str = Field(default="Conservative position sizing", description="Position sizing recommendation")
    key_risk_factor: str = Field(default="Market volatility", description="Primary risk identification")

    # Margin of safety metrics
    margin_of_safety_buffett: float = Field(default=0.20, description="Margin of safety vs Buffett Floor")
    margin_of_safety_min_irr: float = Field(default=0.067, description="Margin of safety vs 10% IRR")
    margin_of_safety_target_irr: float = Field(default=0.27, description="Margin of safety vs 15% IRR")

    def get_all_bands(self) -> list[PriceLadderBand]:
        """Get all price bands as a list."""
        return [self.buffett_floor_band, self.min_irr_band, self.target_irr_band]

    def get_best_action_band(self) -> PriceLadderBand:
        """Get the band with the most attractive action."""
        bands = self.get_all_bands()

        # Priority: STRONG BUY > BUY > CONSIDER > AVOID
        action_priority = {
            'STRONG BUY': 4,
            'BUY': 3,
            'CONSIDER': 2,
            'AVOID': 1
        }

        best_band = max(bands, key=lambda b: max(
            action_priority.get(word, 0) for word in b.action_recommendation.split()
        ))

        return best_band


class ReverseDCFAnalysis(BaseModel):
    """
    Reverse-DCF analysis to understand market-implied expectations.
    
    Per Mauboussin/Rappaport Expectations Investing framework.
    """

    ticker: str = Field(default="", description="Company ticker symbol")
    current_price: float = Field(default=150.0, gt=0.0, description="Current stock price")
    current_fcf_per_share: float = Field(default=12.0, gt=0.0, description="Current FCF per share")

    # Market-implied assumptions
    implied_growth_rate: float = Field(default=0.12, ge=-0.2, le=0.5, description="Growth rate implied by current price")
    implied_terminal_multiple: float = Field(default=0.071, gt=0.0, le=0.2, description="Terminal FCF yield implied")
    implied_fade_period: int = Field(default=10, ge=3, le=15, description="Years until fade to terminal")

    # Agent's assumptions vs market
    agent_growth_rate: float = Field(default=0.10, ge=-0.2, le=0.5, description="Agent's projected growth rate")
    agent_terminal_multiple: float = Field(default=0.083, gt=0.0, le=0.2, description="Agent's terminal multiple")
    agent_fade_period: int = Field(default=10, ge=3, le=15, description="Agent's fade period assumption")

    # Gap analysis
    growth_expectation_gap: float = Field(default=0.02, description="Agent growth - Market implied growth")
    terminal_expectation_gap: float = Field(default=-0.012, description="Agent terminal - Market implied terminal")

    # Market assumptions assessment
    market_assumptions_assessment: str = Field(default="Conservative", description="Reasonable/Optimistic/Pessimistic")
    key_debate_points: list[str] = Field(default_factory=lambda: ["Analysis in markdown file"], description="Key assumption debates")
    catalyst_requirements: list[str] = Field(default_factory=lambda: ["More comprehensive analysis needed"], description="Catalysts needed for agent view")

    @field_validator('growth_expectation_gap')
    @classmethod
    def calculate_growth_gap(cls, v, info):
        """Calculate growth expectation gap."""
        if info.data and 'agent_growth_rate' in info.data and 'implied_growth_rate' in info.data:
            return info.data['agent_growth_rate'] - info.data['implied_growth_rate']
        return v

    @field_validator('terminal_expectation_gap')
    @classmethod
    def calculate_terminal_gap(cls, v, info):
        """Calculate terminal multiple expectation gap."""
        if info.data and 'agent_terminal_multiple' in info.data and 'implied_terminal_multiple' in info.data:
            return info.data['agent_terminal_multiple'] - info.data['implied_terminal_multiple']
        return v

    def get_expectation_summary(self) -> dict[str, str]:
        """Get summary of expectation gaps."""
        growth_direction = "higher" if self.growth_expectation_gap > 0 else "lower"
        terminal_direction = "higher" if self.terminal_expectation_gap > 0 else "lower"

        return {
            'growth_gap_direction': growth_direction,
            'terminal_gap_direction': terminal_direction,
            'overall_stance': self._get_overall_stance()
        }

    def _get_overall_stance(self) -> str:
        """Determine overall stance vs market expectations."""
        if self.growth_expectation_gap > 0.02 and self.terminal_expectation_gap > 0.01:
            return "Significantly more optimistic than market"
        elif self.growth_expectation_gap > 0.01 or self.terminal_expectation_gap > 0.005:
            return "More optimistic than market"
        elif abs(self.growth_expectation_gap) < 0.01 and abs(self.terminal_expectation_gap) < 0.005:
            return "Aligned with market expectations"
        elif self.growth_expectation_gap < -0.01 or self.terminal_expectation_gap < -0.005:
            return "More pessimistic than market"
        else:
            return "Significantly more pessimistic than market"


class StressTestScenario(BaseModel):
    """Individual stress test scenario results."""

    scenario_name: str = Field(default="Conservative Stress", description="Stress test scenario name")
    stress_type: str = Field(default="combined", description="Type of stress (growth, multiple, combined)")
    stress_magnitude: float = Field(default=-0.05, description="Magnitude of stress applied")

    # Results
    stressed_irr: float = Field(default=0.05, description="IRR under stress scenario")
    irr_change: float = Field(default=-0.05, description="IRR change vs base case")
    irr_resilience: bool = Field(default=False, description="Whether IRR stays above 10% threshold")

    # Stress-specific details
    stressed_assumptions: dict[str, Any] = Field(default_factory=lambda: {"fallback": "Conservative estimate"}, description="Assumptions under stress")

    @field_validator('irr_resilience')
    @classmethod
    def check_irr_resilience(cls, v, info):
        """Determine if IRR remains above minimum threshold."""
        if info.data and 'stressed_irr' in info.data:
            return info.data['stressed_irr'] >= 0.10
        return v


class ConservativeStressTestResults(BaseModel):
    """Complete conservative stress testing results."""

    ticker: str = Field(default="", description="Company ticker symbol")
    base_case_irr: float = Field(default=0.0, ge=0.0, description="Base case IRR")

    # Stress scenarios
    stress_scenarios: list[StressTestScenario] = Field(default_factory=list, description="All stress test scenarios")

    # Overall assessment
    resilience_rating: str = Field(default="MODERATE", description="HIGH/MODERATE/LOW resilience rating")
    resilient_scenarios_count: int = Field(default=0, ge=0, description="Number of scenarios with IRR > 10%")
    total_scenarios_count: int = Field(default=1, ge=1, description="Total number of stress scenarios")
    worst_case_irr: float = Field(default=0.0, description="Worst case IRR across all scenarios")
    irr_cushion: float = Field(default=0.0, description="Base case IRR cushion above 10%")

    # Recommendations
    stress_based_recommendation: str = Field(default="", description="Investment recommendation based on stress tests")
    key_vulnerabilities: list[str] = Field(default_factory=list, description="Key vulnerabilities identified")

    @field_validator('resilient_scenarios_count')
    @classmethod
    def count_resilient_scenarios(cls, v, info):
        """Count scenarios where IRR stays above 10%."""
        if info.data and 'stress_scenarios' in info.data:
            return sum(1 for scenario in info.data['stress_scenarios'] if scenario.irr_resilience)
        return v

    @field_validator('total_scenarios_count')
    @classmethod
    def count_total_scenarios(cls, v, info):
        """Count total stress scenarios."""
        if info.data and 'stress_scenarios' in info.data:
            return len(info.data['stress_scenarios'])
        return v

    @field_validator('worst_case_irr')
    @classmethod
    def find_worst_case_irr(cls, v, info):
        """Find worst case IRR across all scenarios."""
        if info.data and 'stress_scenarios' in info.data and info.data['stress_scenarios']:
            return min(scenario.stressed_irr for scenario in info.data['stress_scenarios'])
        return v

    def get_resilience_ratio(self) -> float:
        """Calculate resilience ratio (resilient / total scenarios)."""
        return self.resilient_scenarios_count / self.total_scenarios_count if self.total_scenarios_count > 0 else 0.0


class OwnerReturnsValuation(BaseModel):
    """
    Complete Owner-Returns FCF/Share valuation analysis.
    
    Integrates all components of elite investor methodology:
    - IRR decomposition
    - FCF/share projections  
    - Price Ladder analysis
    - Reverse-DCF expectations
    - Conservative stress testing
    """

    # Basic information
    ticker: str = Field(default="", description="Company ticker symbol")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    current_price: float = Field(default=100.0, gt=0.0, description="Current stock price")
    analyst_name: str = Field(default="ValuationAgent", description="Analyst/agent name")

    # Core analysis components - with defaults for MVP
    irr_analysis: IRRComponents | None = Field(default=None, description="IRR decomposition analysis")
    fcf_projections: FCFProjections | None = Field(default=None, description="FCF per share projections")
    price_ladder: PriceLadderAnalysis | None = Field(default=None, description="Price Ladder analysis")
    reverse_dcf: ReverseDCFAnalysis | None = Field(default=None, description="Reverse-DCF expectations analysis")
    stress_tests: ConservativeStressTestResults | None = Field(default=None, description="Conservative stress testing")

    # Financial metrics (still useful for context)
    financial_ratios: dict[str, Any] | None = Field(None, description="Supporting financial ratios")
    peer_analysis: dict[str, Any] | None = Field(None, description="Peer comparison context")

    # Final investment thesis - with defaults for MVP
    investment_thesis: str = Field(default="", description="Complete investment thesis")
    final_recommendation: str = Field(default="", description="Final investment recommendation")
    confidence_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Analyst confidence (0-1)")
    key_risks: list[str] = Field(default_factory=list, description="Key investment risks")
    key_opportunities: list[str] = Field(default_factory=list, description="Key investment opportunities")

    # Data sources and citations
    data_sources: list[str] = Field(default_factory=list, description="All data source citations")
    methodology_notes: str = Field(default="Owner-Returns FCF/Share Framework", description="Methodology used")

    def get_total_irr(self) -> float:
        """Get total IRR from components."""
        return self.irr_analysis.calculate_total_irr() if self.irr_analysis else 0.08

    def get_best_price_band(self) -> PriceLadderBand:
        """Get the most attractive price band."""
        return self.price_ladder.get_best_action_band() if self.price_ladder else PriceLadderBand()

    def get_investment_summary(self) -> dict[str, Any]:
        """Get concise investment summary."""
        return {
            'ticker': self.ticker,
            'current_price': self.current_price,
            'total_irr': self.get_total_irr(),
            'recommendation': self.final_recommendation,
            'confidence': self.confidence_level,
            'best_price_band': self.get_best_price_band().action_recommendation,
            'stress_resilience': self.stress_tests.resilience_rating if self.stress_tests else 'MODERATE',
            'market_stance': self.reverse_dcf.get_expectation_summary()['overall_stance'] if self.reverse_dcf else 'Aligned with market'
        }


class ValuationContext(BaseModel):
    """Context for valuation analysis execution."""

    session_id: str = Field(default="", description="Session identifier")
    ticker: str = Field(default="", description="Company ticker being analyzed")
    expertise_level: int = Field(default=5, ge=1, le=10, description="User expertise level")
    analysis_depth: str = Field(default="intermediate", description="Analysis depth (foundational/educational/intermediate/advanced/executive)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Analysis creation timestamp")
    reasoning_effort: str = Field(default="medium", description="GPT-5 reasoning effort level")

    # Web search and research context
    web_search_data: dict[str, Any] | None = Field(None, description="GPT-5 web search results")
    citations: list[str] = Field(default_factory=list, description="Data source citations")

    # Analysis parameters
    conservative_bias: bool = Field(default=True, description="Apply conservative bias to assumptions")
    stress_testing: bool = Field(default=True, description="Include conservative stress testing")
    reverse_dcf_analysis: bool = Field(default=True, description="Include reverse-DCF expectations analysis")

    def get_output_detail_level(self) -> str:
        """Determine output detail level based on expertise."""
        if self.expertise_level <= 2:
            return "foundational"  # Maximum educational content
        elif self.expertise_level <= 4:
            return "educational"  # Detailed explanations
        elif self.expertise_level <= 6:
            return "intermediate"  # Balanced analysis
        elif self.expertise_level <= 8:
            return "advanced"  # Sophisticated analysis
        else:
            return "executive"  # Expert summaries
