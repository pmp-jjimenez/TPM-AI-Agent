from datetime import datetime
from typing import List, Literal

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


class IntelligenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    program_id: str
    generated_at: datetime
    source: Literal["ai", "deterministic_fallback"]
    routing: RoutingModel
    summary: str
    attention_items: List[str]
    risks: List[str]
    missing_information: List[str]
    recommended_actions: List[str]
    confidence: Literal["High", "Medium", "Low"]
    limitations: List[str]
