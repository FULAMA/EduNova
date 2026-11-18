from uuid import UUID

from pydantic import BaseModel, Field


class ReportCardAIFeedbackResponse(BaseModel):
    report_card_id: UUID = Field(..., description="Identifiant du bulletin")
    student_name: str = Field(..., description="Nom complet de l'élève")
    encouraging: str = Field(..., description="Appréciation bienveillante et encourageante")
    analytical: str = Field(..., description="Appréciation équilibrée avec points forts et axes d'effort")
    demanding: str = Field(..., description="Appréciation exigeante orientée objectifs et rigueur")


class EarlyWarningAIDiagnosisResponse(BaseModel):
    student_id: UUID = Field(..., description="Identifiant de l'élève")
    student_name: str = Field(..., description="Nom complet de l'élève")
    academic_period_id: UUID = Field(..., description="Identifiant de la période académique")
    risk_level: str = Field(..., description="Niveau de risque (LOW, MEDIUM, HIGH)")
    risk_score: int = Field(..., description="Score de risque de 0 à 100")
    diagnostic_summary: str = Field(..., description="Synthèse explicative du risque de décrochage")
    root_causes: list[str] = Field(..., description="Causes racines identifiées")
    action_plan: list[str] = Field(..., description="Plan d'actions et remédiations recommandées")


class ParentPortalAISummaryResponse(BaseModel):
    student_id: UUID = Field(..., description="Identifiant de l'enfant")
    report_card_id: UUID = Field(..., description="Identifiant du bulletin officiel")
    period_name: str = Field(..., description="Nom de la période scolaire")
    headline: str = Field(..., description="Titre synthétique de l'évaluation")
    summary: str = Field(..., description="Explication vulgarisée et bienveillante pour les parents")
    tips_for_home: list[str] = Field(..., description="Conseils pratiques d'accompagnement à la maison")
