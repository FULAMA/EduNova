import json
import logging
import os
from typing import Any
import urllib.error
import urllib.request

from src.academic.application.interfaces.ai_pedagogical_service import AIPedagogicalService

logger = logging.getLogger(__name__)


class EduNovaAIPedagogicalService(AIPedagogicalService):
    """Service d'intelligence artificielle pédagogique pour EduNova.

    Supporte l'API Google Gemini avec repli déterministe automatique
    (moteur heuristique pédagogique hors-ligne) en cas d'absence de clé ou d'erreur réseau.
    """

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("EDUNOVA_AI_API_KEY")
        self._model = model

    def generate_report_card_feedback(
        self,
        student_name: str,
        general_average: float,
        subject_results: list[dict[str, Any]],
        deliberation_decision: str,
    ) -> dict[str, str]:
        if self._api_key:
            try:
                result = self._call_gemini_feedback(student_name, general_average, subject_results, deliberation_decision)
                if result:
                    return result
            except Exception as exc:
                logger.warning("Échec de l'appel Gemini feedback, repli sur le moteur heuristique : %s", exc)

        return self._rule_based_feedback(student_name, general_average, subject_results, deliberation_decision)

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
        if self._api_key:
            try:
                result = self._call_gemini_risk(student_name, risk_level, risk_score, reasons, general_average, attendance_rate, unjustified_absences)
                if result:
                    return result
            except Exception as exc:
                logger.warning("Échec de l'appel Gemini risk, repli sur le moteur heuristique : %s", exc)

        return self._rule_based_risk(student_name, risk_level, risk_score, reasons, general_average, attendance_rate, unjustified_absences)

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
        if self._api_key:
            try:
                result = self._call_gemini_parent(student_name, period_name, general_average, deliberation_decision, strong_points, focus_areas, attendance_summary)
                if result:
                    return result
            except Exception as exc:
                logger.warning("Échec de l'appel Gemini parent, repli sur le moteur heuristique : %s", exc)

        return self._rule_based_parent(student_name, period_name, general_average, deliberation_decision, strong_points, focus_areas, attendance_summary)

    # =========================================================================
    # MOTEURS HEURISTIQUES PÉDAGOGIQUES (100% Hors-ligne / Déterministes)
    # =========================================================================

    def _rule_based_feedback(
        self, student_name: str, avg: float, results: list[dict[str, Any]], decision: str
    ) -> dict[str, str]:
        strong_subjs = [r.get("subject_name", "une discipline") for r in results if r.get("average", 0) >= 13]
        weak_subjs = [r.get("subject_name", "une discipline") for r in results if r.get("average", 0) < 10]

        strong_str = ", ".join(strong_subjs[:2]) if strong_subjs else "son assiduité"
        weak_str = ", ".join(weak_subjs[:2]) if weak_subjs else "le maintien de la rigueur"

        if avg >= 14:
            encouraging = (
                f"Excellent trimestre pour {student_name} ({avg:.1f}/20). "
                f"Une dynamique remarquable portée par de solides acquis en {strong_str}. Félicitations du conseil !"
            )
            analytical = (
                f"Bilan très positif avec une moyenne de {avg:.1f}/20 ({decision}). "
                f"Points d'appui majeurs en {strong_str}. Pour viser l'excellence, approfondir {weak_str}."
            )
            demanding = (
                f"Très bons résultats ({avg:.1f}/20). {student_name} a un potentiel manifeste : "
                f"il convient de maintenir cette régularité sans relâcher la participation active."
            )
        elif avg >= 10:
            encouraging = (
                f"Trimestre encourageant pour {student_name} avec {avg:.1f}/20. "
                f"De réels efforts constatés en {strong_str}. En maintenant ce cap, les progrès seront encore plus nets."
            )
            analytical = (
                f"Trimestre satisfaisant ({avg:.1f}/20, décision : {decision}). "
                f"Des bases solides en {strong_str}, mais des fragilités à consolider rapidement en {weak_str}."
            )
            demanding = (
                f"Ensemble convenable mais perfectible ({avg:.1f}/20). "
                f"{student_name} doit intensifier le travail personnel en {weak_str} pour sécuriser son parcours."
            )
        else:
            encouraging = (
                f"Trimestre difficile pour {student_name} ({avg:.1f}/20), mais des capacités existent, notamment en {strong_str}. "
                f"L'équipe pédagogique est mobilisée pour l'accompagner vers le redressement."
            )
            analytical = (
                f"Résultats insuffisants ({avg:.1f}/20, décision : {decision}). "
                f"Des lacunes accumulées en {weak_str} compromettent l'équilibre académique. Un plan de remédiation s'impose."
            )
            demanding = (
                f"Bilan insuffisant ({avg:.1f}/20). Un sursaut impératif et immédiat est attendu en {weak_str}. "
                f"Rigueur et présence assidue indispensables dès le prochain trimestre."
            )

        return {
            "encouraging": encouraging,
            "analytical": analytical,
            "demanding": demanding,
        }

    def _rule_based_risk(
        self,
        student_name: str,
        risk_level: str,
        risk_score: int,
        reasons: list[str],
        avg: float,
        att_rate: float,
        absences: int,
    ) -> dict[str, Any]:
        if risk_level == "HIGH":
            summary = (
                f"Alerte précoce critique pour {student_name} (Indicateur de risque : {risk_score}/100 - Élevé). "
                f"La moyenne générale de {avg:.1f}/20 combinée à {absences} absence(s) injustifiée(s) "
                f"expose l'élève à un décrochage imminent sans action corrective urgente."
            )
            actions = [
                "Organiser un entretien tripartite immédiat (Direction, Responsables légaux, Élève).",
                "Mettre en place un tutorat disciplinaire hebdomadaire sur les matières en échec.",
                "Instaurer un suivi quotidien d'assiduité avec signature du carnet de correspondance.",
                "Adapter le plan de devoirs et fournir des fiches de synthèse de rattrapage.",
            ]
        elif risk_level == "MEDIUM":
            summary = (
                f"Vigilance pédagogique requise pour {student_name} (Indicateur de risque : {risk_score}/100 - Modéré). "
                f"Moyenne de {avg:.1f}/20 et assiduité de {att_rate:.1f}%. Des signes d'essoufflement sont perceptibles."
            )
            actions = [
                "Convoquer l'élève pour un bilan d'étape avec le professeur principal.",
                "Proposer des séances d'aide aux devoirs les mercredis ou fins de journée.",
                "Alerter les parents par courrier ou notification sur le portail numérique.",
            ]
        else:
            summary = (
                f"Trajectoire académique stable pour {student_name} (Indicateur de risque : {risk_score}/100 - Faible). "
                f"Moyenne générale de {avg:.1f}/20 et assiduité exemplaire ({att_rate:.1f}%)."
            )
            actions = [
                "Poursuivre l'accompagnement régulier et encourager l'excellence.",
                "Valoriser l'élève comme tuteur pair auprès des camarades en difficulté.",
            ]

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "diagnostic_summary": summary,
            "root_causes": reasons if reasons else ["Fléchissement périodique des résultats"],
            "action_plan": actions,
        }

    def _rule_based_parent(
        self,
        student_name: str,
        period_name: str,
        avg: float,
        decision: str,
        strong_points: list[str],
        focus_areas: list[str],
        attendance_summary: str,
    ) -> dict[str, Any]:
        strong_str = ", ".join(strong_points[:2]) if strong_points else "l'implication générale"
        focus_str = ", ".join(focus_areas[:2]) if focus_areas else "la régularité dans les révisions"

        if avg >= 14:
            headline = f"Félicitations : Un excellent {period_name} pour {student_name}"
            summary = (
                f"Chers parents, votre enfant {student_name} a réalisé un très beau parcours ce trimestre avec une moyenne "
                f"générale de {avg:.1f}/20. Ses performances sont particulièrement remarquables en {strong_str}. "
                f"{attendance_summary}. L'école le félicite chaleureusement !"
            )
            tips = [
                "Féliciter votre enfant pour ses efforts et valoriser sa rigueur de travail.",
                "Encourager la lecture autonome pour enrichir son vocabulaire et sa culture générale.",
                "Maintenir un rythme de repos équilibré les week-ends.",
            ]
        elif avg >= 10:
            headline = f"Bilan du {period_name} : Résultats satisfaisants et réguliers"
            summary = (
                f"Chers parents, le trimestre de {student_name} est positif avec une moyenne de {avg:.1f}/20. "
                f"Des bases solides sont posées en {strong_str}. Toutefois, une attention particulière doit être portée "
                f"sur {focus_str} pour progresser encore davantage. {attendance_summary}."
            )
            tips = [
                "Consacrer 45 minutes par jour à la relecture calme des leçons de la journée.",
                "Vérifier régulièrement le carnet de correspondance et les devoirs en avance.",
                "Ne pas hésiter à solliciter les professeurs lors des permanences pédagogiques.",
            ]
        else:
            headline = f"Bilan du {period_name} : Des difficultés nécessitant un soutien attentif"
            summary = (
                f"Chers parents, ce {period_name} a été exigeant pour {student_name} ({avg:.1f}/20). "
                f"Des lacunes sont apparues en {focus_str}. L'équipe éducative reste pleinement à vos côtés "
                f"pour inverser cette tendance dès le prochain trimestre. {attendance_summary}."
            )
            tips = [
                "Établir un planning d'étude quotidien structuré et sans écrans à la maison.",
                "Contacter le préfet ou les enseignants des matières en difficulté pour un plan d'aide.",
                "Encourager l'enfant et dédramatiser pour lui redonner confiance en ses capacités.",
            ]

        return {
            "headline": headline,
            "summary": summary,
            "tips_for_home": tips,
        }

    # =========================================================================
    # INTÉGRATION API GOOGLE GEMINI (SI CLÉ PRÉSENTE)
    # =========================================================================

    def _call_gemini_feedback(self, student_name: str, avg: float, results: list[dict], decision: str) -> dict[str, str] | None:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        prompt = f"""Tu es un conseiller pédagogique expert dans un établissement scolaire d'excellence.
Rédige 3 variantes d'appréciations de bulletin pour l'élève {student_name} (Moyenne : {avg}/20, Décision conseil : {decision}).
Résultats par discipline : {json.dumps(results, ensure_ascii=False)}.
Réponds STRICTEMENT sous format JSON avec ces 3 clés :
- "encouraging": appréciation bienveillante et motivante
- "analytical": appréciation équilibrée avec points forts et points d'appui
- "demanding": appréciation exigeante orientée vers le travail à fournir"""
        return self._post_gemini(url, prompt)

    def _call_gemini_risk(self, name: str, level: str, score: int, reasons: list[str], avg: float, att: float, absences: int) -> dict[str, Any] | None:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        prompt = f"""Tu es le préfet des études d'un établissement scolaire.
Établis un diagnostic pédagogique de risque d'échec pour {name} :
Niveau de risque : {level} (Score : {score}/100), Moyenne : {avg}/20, Taux présence : {att}%, Absences injustifiées : {absences}.
Motifs détectés : {reasons}.
Réponds STRICTEMENT sous format JSON avec ces 3 clés :
- "diagnostic_summary": paragraphe d'analyse clair de la situation de l'élève
- "root_causes": liste des causes probables
- "action_plan": liste de 3 à 4 actions de remédiation concrètes"""
        return self._post_gemini(url, prompt)

    def _call_gemini_parent(self, name: str, period: str, avg: float, decision: str, strong: list, focus: list, att: str) -> dict[str, Any] | None:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        prompt = f"""Tu rédiges une synthèse de bulletin bienveillante et compréhensible destinée aux parents de l'élève {name} pour le {period}.
Moyenne : {avg}/20, Décision : {decision}.
Points forts : {strong}. Points d'effort : {focus}. Présence : {att}.
Réponds STRICTEMENT sous format JSON avec ces 3 clés :
- "headline": titre valorisant et clair
- "summary": paragraphe chaleureux et explicatif sans jargon scolaire
- "tips_for_home": liste de 3 conseils pratiques à appliquer à la maison"""
        return self._post_gemini(url, prompt)

    def _post_gemini(self, url: str, prompt: str) -> dict[str, Any] | None:
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            candidate = payload["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(candidate)
