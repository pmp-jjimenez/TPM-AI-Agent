from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class PersonaModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    display_name: str


class RoutingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str
    primary_persona: PersonaModel
    supporting_personas: List[PersonaModel]


Confidence = Literal["High", "Medium", "Low"]
Priority = Literal["Critical", "High", "Medium", "Low"]


class IntelligenceFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: Literal["fact", "missing_information", "assumption", "risk", "dependency", "conflict"]
    statement: str
    confidence: Confidence
    evidence_refs: List[str]
    impact: Optional[str] = None


class IntelligenceRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    priority: Priority
    statement: str
    rationale: str
    evidence_refs: List[str]
    related_finding_ids: List[str]


class IntelligenceDecisionRequired(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    priority: Priority
    statement: str
    reason: str
    related_finding_ids: List[str]
    related_recommendation_ids: List[str]


class IntelligenceNextAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    priority: Priority
    statement: str
    rationale: str
    related_finding_ids: List[str]
    related_recommendation_ids: List[str]


class IntelligenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    program_id: str
    schema_version: Literal["1.0.0"]
    generated_at: datetime
    source: Literal["ai", "deterministic_fallback"]
    routing: RoutingModel
    summary: str
    confidence: Confidence
    findings: List[IntelligenceFinding]
    recommendations: List[IntelligenceRecommendation]
    decisions_required: List[IntelligenceDecisionRequired]
    next_action: IntelligenceNextAction
    limitations: List[str]
