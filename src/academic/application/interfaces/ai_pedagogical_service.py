from abc import ABC, abstractmethod
from typing import Any


class AIPedagogicalService(ABC):
    @abstractmethod
    def generate_report_card_feedback(
        self,
        student_name: str,
        general_average: float,
        subject_results: list[dict[str, Any]],
        deliberation_decision: str,
    ) -> dict[str, str]:
        """Génère 3 variantes d'appréciations pédagogiques pour le bulletin :

        - 'encouraging': bienveillante et motivante
        - 'analytical': structurée, axée sur les points forts et faibles
        - 'demanding': exigeante avec objectifs de travail clairs
        """
        ...

    @abstractmethod
    def generate_early_warning_diagnosis(
        self,
        student_name: str,
        risk_level: str,
        risk_score: int,
        reasons: list[str],
        general_average: float,
        attendance_rate: float,
        unjustified_absences: int,
    ) -> dict[str, Any]:
        """Génère un diagnostic de décrochage pour la direction et les enseignants :

        - 'diagnostic_summary': synthèse en langage clair du profil de risque
        - 'root_causes': liste des facteurs de risque identifiés
        - 'action_plan': recommandations concrètes de remédiation
        """
        ...

    @abstractmethod
    def generate_parent_summary(
        self,
        student_name: str,
        period_name: str,
        general_average: float,
        deliberation_decision: str,
        strong_points: list[str],
        focus_areas: list[str],
        attendance_summary: str,
    ) -> dict[str, Any]:
        """Génère une synthèse pédagogique vulgarisée pour le portail parent :

        - 'headline': titre synthétique
        - 'summary': explication bienveillante du trimestre
        - 'tips_for_home': conseils pratiques pour accompagner l'enfant à la maison
        """
        ...
