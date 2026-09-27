from src.academic.domain.value_objects.academic_risk import (
    AcademicRisk,
    RiskLevel,
)


class AcademicRiskAnalyzer:

    def analyze(
        self,
        average: float,
        attendance_rate: float,
        unjustified_absences: int,
    ) -> AcademicRisk:

        score = 0
        reasons = []

        # -----------------------------
        # Performance académique
        # -----------------------------

        if average < 10:
            score += 40
            reasons.append(
                "Moyenne générale inférieure au seuil de réussite."
            )

        if average < 8:
            score += 20
            reasons.append(
                "Moyenne générale particulièrement faible."
            )

        # -----------------------------
        # Assiduité
        # -----------------------------

        if attendance_rate < 80:
            score += 20
            reasons.append(
                "Taux d'assiduité inférieur à 80 %."
            )

        if attendance_rate < 60:
            score += 10
            reasons.append(
                "Taux d'assiduité critique."
            )

        # -----------------------------
        # Absences injustifiées
        # -----------------------------

        if unjustified_absences >= 5:
            score += 20
            reasons.append(
                "Nombre élevé d'absences injustifiées."
            )

        # -----------------------------
        # Sécurité : score maximum
        # -----------------------------

        score = min(score, 100)

        # -----------------------------
        # Classification du risque
        # -----------------------------

        if score <= 30:
            level = RiskLevel.LOW

        elif score <= 70:
            level = RiskLevel.MEDIUM

        else:
            level = RiskLevel.HIGH

        # -----------------------------
        # Aucun risque détecté
        # -----------------------------

        if not reasons:
            reasons.append(
                "Aucun indicateur majeur de risque détecté."
            )

        return AcademicRisk(
            level=level,
            score=score,
            reasons=tuple(reasons),
        )
