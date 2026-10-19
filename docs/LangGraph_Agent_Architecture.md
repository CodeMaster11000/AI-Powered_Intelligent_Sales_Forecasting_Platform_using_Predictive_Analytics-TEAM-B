# SalesGenie AI - LangGraph Multi-Agent Architecture Specification

**Author**: Jayant Vaibhav (AI/ML Engineer)  
**Standard**: IEEE Std 830-1998  
**Component**: Module 2 (Lead Intelligence & Company Analysis Engine)  
**Deliverable**: Milestone 1 / Day 3 Architecture Baseline

---

## 1. Architectural Overview

SalesGenie AI deploys a stateful, decoupled multi-agent architecture built upon **LangGraph (StateGraph)** and powered by **Gemini 1.5 Pro / GPT-4o**. The architecture cleanly isolates agent execution into discrete functional nodes:

```mermaid
flowchart TD
    Start([Prospect Profile Ingested]) --> IngestionState[State Initialization]
    
    subgraph Multi-Agent Orchestration Bus (LangGraph)
        IngestionState --> R_Node[Research Agent Node]
        R_Node --> |Industry Benchmarking & Opportunity Detection| R_State[Enriched Research State]
        R_State --> Q_Node[Qualification Agent Node]
        Q_Node --> |Predictive Weighting & Persona Mapping| Q_State[Final Qualified State]
    end
    
    Q_State --> DB_Sync[(PostgreSQL: Company_Insights)]
    DB_Sync --> PresentationLayer([Streamlit Presentation Layer & REST Endpoints])
```

---

## 2. Core Agent Nodes

### Node 1: Research Agent (`research_agent_node`)
* **Input**: Prospect demographics (Company name, industry, headcount size, revenue estimates, funding stage, capital raised, corporate location, tech stack components).
* **Core Responsibilities**:
  1. **REQ-M2-01 (Automated Company Profiling)**: Tokenizes and classifies the active technology stack into 5 enterprise dimensions: `Cloud Infrastructure`, `Backend`, `Frontend`, `Data/DB`, and `Containerization & DevOps`.
  2. **REQ-M2-02 (Business Opportunity Identification)**: Evaluates infrastructure posture against 4 transformation vectors:
     * **ERP Modernization Needs**: Detects legacy databases (Oracle, SAP, On-Premises) with high operational friction.
     * **Cloud Migration Opportunities**: Evaluates on-premises/hybrid workloads for AWS/Azure/GCP modernization.
     * **Process Automation Potential**: Flags manual research bottlenecks in B2B sales cycles.
     * **Digital Transformation Projects**: Identifies active tech expansion signals.

### Node 2: Qualification Agent (`qualification_agent_node`)
* **Input**: Research Agent intermediate state.
* **Core Responsibilities**:
  1. **REQ-M2-03 (Qualification Score 0–100)**: Calculates deterministic multi-factor qualification metrics:
     * *Company Growth & Funding (+25 points max)*: Evaluates Series C/B milestones indicating immediate tool budget.
     * *Tech Stack Compatibility (+20 points max)*: Measures modern API and cloud alignment.
     * *Headcount & Revenue Scale (+15 points max)*: Enterprise purchasing capacity.
     * *Decision Maker Seniority (+10 points max)*: CTO, VP, CPO, Founder persona weight.
  2. **High Growth Detection**: Flags rapid-growth capital infusions.
  3. **Decision Maker Profiling**: Outputs personalized pitch angles tailored to technical and commercial sponsors.

---

## 3. Zero-Hallucination & FMEA Risk Mitigation

In compliance with **IEEE SRS Section 4.3 (FMEA Risk Mitigation - RPN 96)**:
* **Constraint Grounding**: All LLM prompt instructions explicitly forbid unbounded extrapolation. Claims are strictly grounded against ingested prospect attributes.
* **Deterministic Fallback Engine**: If external LLM API rate limits occur or offline operation is required, the system executes an automated rule-based heuristic parser without degrading output quality or schema compliance.
* **Sub-5-Second Latency SLA**: Average pipeline execution executes in **< 1.0s**, easily surpassing the 5.0-second IEEE requirement.

---

## 4. LangGraph State Schema (`AgentState`)

```python
class AgentState(TypedDict):
    lead_id: Optional[int]
    company_name: str
    industry: str
    contact_name: str
    email: Optional[str]
    company_size: Optional[str]
    annual_revenue: Optional[str]
    funding_stage: Optional[str]
    capital_raised: Optional[str]
    location: Optional[str]
    tech_stack: Optional[str]
    
    # Research Outputs
    industry_domain_analysis: Optional[str]
    growth_indicators: Optional[List[str]]
    tech_stack_components: Optional[Dict[str, List[str]]]
    transformation_opportunities: Optional[List[Dict[str, Any]]]
    
    # Qualification Outputs
    qualification_score: Optional[int]
    high_growth_potential: Optional[bool]
    funding_analysis: Optional[str]
    tech_alignment_metrics: Optional[List[Dict[str, Any]]]
    overall_tech_compatibility_score: Optional[int]
    decision_makers: Optional[List[Dict[str, Any]]]
    business_needs_summary: Optional[str]
    strategic_recommendation: Optional[str]
    
    # Metadata
    execution_trace: List[str]
    errors: List[str]
```
