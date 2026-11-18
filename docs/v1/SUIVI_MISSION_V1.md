# Suivi mission V1 — parcours métier et contrats API

Dernière mise à jour : 2026-11-04

## Tranche livrée dans cette session

1. Baseline + matrice (`MATRICE_TRACABILITE_V1.md`)
2. `POST /auth/logout` (révocation refresh compatible)
3. `PUT /students/{id}`
4. `GET /billing/payments` (pagination + filtres)
5. `GET /billing/arrears` (calcul depuis obligations / paiements confirmés)
6. `GET /dashboard/direction` (indicateurs réels Décision 23)
7. Déconnexion frontend via appel logout
8. Tests ciblés + documentation contrats

## Restant prioritaire

| Lot | Reste | Motif |
|---|---|---|
| 3 | Accès directory PROF / PARENT / STUDENT distinct | Pas de modèle d’affectation PROF ; PARENT bloqué métier |
| 5 | Rappels d’impayés, échéanciers multi-tranches configurables | Déc. 22 partiellement couverte (calcul arriérés) ; rappels non démarrés |
| 6 | UI dashboard direction branchée sur la nouvelle API | Backend prêt ; FE encore sur agrégation locale |
| 7 | Portail enseignant | Aucune entité TeacherAssignment dans le code |
| 8 | Portail parent | PAR-REL-* `PROPOSED - BLOCKED` |
| 9 | Élargir rôles bulletins, révocation, audit | BUL-TECH-02..06 en attente d’arbitrage |
| 10 | Suite CI complète hors cibles de la session | À relancer après merges |

## Arbitrages demandés au product owner

Voir section « Décisions métier » du rapport final de session.
