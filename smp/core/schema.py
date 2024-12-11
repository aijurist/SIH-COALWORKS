from dataclasses import dataclass, field
from typing import List, Dict
from langchain_core.pydantic_v1 import Field, BaseModel

class MitigationStep(BaseModel):
    description: str = Field(description="Detailed description of the additional control measures.")
    responsible_party: str = Field(description="The party responsible for implementing this mitigation step.", max_length=1)
    priority: str = Field(description="The priority level of the mitigation step (e.g., 'High', 'Medium', 'Low').")


class HazardDetails(BaseModel):
    hazard_id: str = Field(description="A unique identifier for the hazard (e.g., 'GL-1' for Gas Leakage, 'BO-2' for Blasting Operation).")
    hazard_aspect: str = Field(description="The specific hazard or environmental aspect identified in the activity.")
    possible_outcome: str = Field(description="The potential consequences of the hazard (e.g., injury, property damage).")
    existing_control_measures: str = Field(description="Current safety measures or protocols in place to manage the hazard.")
    probability: int = Field(description="The likelihood of the hazard occurring, based on a numeric scale.")
    exposure: int = Field(description="The frequency or level of exposure to the hazard, represented on a numeric scale.")
    consequences: int = Field(description="The potential severity of the consequences if the hazard occurs, on a numeric scale.")
    risk_score: int = Field(description="The calculated risk score, based on the formula: Risk Score = Probability * Exposure * Consequences.")
    risk_rating: str = Field(description="The risk level derived from the risk score, typically categorized (e.g., 'Low', 'Medium', 'High').")
    additional_control_measures: List[MitigationStep] = Field(description="New or additional measures to control the hazard (maximum of 2 items).", max_items=2)
    residual_impact: str = Field(description="The remaining risk level after applying additional control measures (e.g., 'Low', 'Medium', 'High').")


class SMPModel(BaseModel):
    activity_name: str = Field(description="The name of the activity being analyzed.")
    hazards: List[HazardDetails] = Field(description="A list of hazards and their detailed analysis for the activity.")
