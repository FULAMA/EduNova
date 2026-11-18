# Contrats API — Paiements globaux et arriérés

## `GET /billing/payments`

Rôles : `ADMIN`, `DIRECTION`, `ACCOUNTANT`, `CASHIER`.

Query :

| Paramètre | Description |
|---|---|
| `student_id` | Filtre élève (404 si hors tenant) |
| `class_id` | Élèves avec affectation `ACTIVE` dans la classe |
| `status` | Statut paiement (`CONFIRMED`, …) |
| `recorded_from` / `recorded_to` | Période (date locale ISO) |
| `limit` | 1–200 (défaut 50) |
| `offset` | ≥ 0 |

Réponse : `{ items, total, limit, offset }` — même forme de paiement que le journal / summary.

Isolation : `tenant_id` du JWT/membership uniquement.

## `GET /billing/arrears`

Rôles finance identiques.

Calcule pour chaque charge `OPEN` :

- `amount_due` = montant de la charge
- `amount_paid` = paiements `CONFIRMED` − contre-écritures
- `amount_remaining` = due − paid (uniquement si > 0)
- `overdue` = `due_date < as_of` (défaut : aujourd’hui)

Query : `student_id`, `class_id`, `as_of`, `overdue_only` (défaut true), pagination.

Aucune modification d’historique. Aucune génération de frais à l’inscription.

## `GET /dashboard/direction`

Rôles : `ADMIN`, `DIRECTION`.

Indicateurs calculés depuis les données persistées (élèves actifs, effectifs par classe, montants attendus / payés / restants, taux de recouvrement par devise, situation par classe). Jamais de valeurs simulées.
