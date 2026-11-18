# Blocages lots 7–9 — EduNova V1

## LOT 7 — Portail enseignant

**Statut : BLOQUÉ — pas d’implémentation productive**

Faits vérifiés :

- Aucun rôle `PROF` dans `require_role(...)` des routes.
- Aucune table / entité d’affectation enseignant → classe / matière.
- `StudentAssignment` relie un élève à une classe, pas un professeur.
- Les tests existants traitent `TEACHER` comme rôle refusé (403) sur finance / élèves.

Sans modèle d’affectation et sans décision métier validée sur les permissions de saisie de notes, toute API « classes de l’enseignant » serait inventée.

**Prochaine étape après arbitrage :** définir `TeacherAssignment` (tenant, user, class, subject, period) + migrations + contrôles backend.

## LOT 8 — Portail parent

**Statut : BLOQUÉ — décisions PAR-REL `PROPOSED - BLOCKED`**

Référence : `docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md` et `docs/reports/RAPPORT_PREPARATION_MODELE_PARENT_ENFANT_2026-10-22.md`.

`StudentUserLink` ≠ parent-enfant (cardinalités incompatibles).

Aucune route, migration ou permission parent n’a été activée dans cette mission (conforme aux règles : ne pas inventer de relation sur un `student_id` client).

## LOT 9 — Bulletins

**Statut : PARTIELLEMENT LIVRÉ (existant)**

Déjà en place :

- Préparation / publication / correction / consultation / PDF
- Statuts `DRAFT` / `ISSUED` / `SUPERSEDED`
- Portail élève limité aux bulletins officiels

Ouvert (ne pas décider arbitrairement) :

- `BUL-TECH-02` rôles de publication (ADMIN seul aujourd’hui)
- `BUL-TECH-03` consultation des versions remplacées
- `BUL-TECH-04` révocation
- `BUL-TECH-05` rétention PDF
- `BUL-TECH-06` contrat d’audit
