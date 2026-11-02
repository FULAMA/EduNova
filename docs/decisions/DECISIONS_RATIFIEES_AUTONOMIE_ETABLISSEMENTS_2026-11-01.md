# Décisions ratifiées — Autonomie des établissements EduNova

- Statut : VALIDÉES PAR LE PROPRIÉTAIRE DU PRODUIT
- Date de ratification : 2026-11-01
- Propriétaire métier : propriétaire du produit EduNova
- Référence : validation explicite des recommandations dans la conversation du 2026-11-01
- Portée : décisions de cadrage à intégrer au registre canonique ; elles n'autorisent pas à inventer des exigences réglementaires.

## EDN-ARCH-001 — Autonomie de configuration par établissement

**Statut : VALIDÉE**

Chaque établissement dispose de son propre cadre organisationnel et opérationnel. Il configure ses politiques académiques, financières, administratives et ses workflows dans les limites des règles légales applicables et des garanties de sécurité, d'intégrité, de confidentialité et de traçabilité imposées par EduNova.

Les configurations sont isolées par tenant, versionnées, datées, modifiables par les personnes habilitées et conservées dans l'historique. Une modification de politique ne réinterprète ni ne recalcule silencieusement les données historiques.

### Invariants non configurables par un établissement

- Isolation stricte des tenants et contrôle d'accès côté serveur.
- Intégrité référentielle, transactions, idempotence et protection contre les doubles traitements.
- Audit des opérations sensibles et conservation de l'historique métier.
- Confidentialité, minimisation des données et protection des secrets.
- Séparation des environnements et contrôle des migrations.
- Respect des obligations légales et réglementaires applicables à l'établissement.
- Aucune élévation de privilège ou permission hors du périmètre du tenant.

L'autonomie ne signifie donc pas la possibilité de désactiver les garde-fous de la plateforme ou de contourner la loi.

## Décisions V1 ratifiées

| Référence | Choix ratifié | Règle et limites |
|---|---|---|
| D1 — Années ouvertes | A | Une seule année scolaire ouverte par tenant en V1. Les années historiques restent consultables. |
| D2 — Autorisations administratives | C | Séparer l'administration technique de la plateforme et les responsabilités métier de l'établissement. Les permissions métier sont explicites, tenant-scoped et contrôlées côté serveur. Ne pas accorder automatiquement tous les droits à un rôle par simple héritage. |
| D3 — Périodes chevauchantes | B | Chevauchement autorisé uniquement entre calendriers/programmes distincts explicitement identifiés. Les périodes d'un même calendrier ne se chevauchent pas, sauf règle métier future documentée. |
| D4 — Identification des personnes | A | Identifiant interne EduNova, conservation des matricules existants comme références, signalement des doublons possibles et fusion uniquement après vérification humaine. |
| D5 — Surpaiement | B | Le surplus confirmé devient un crédit traçable au compte de l'élève. Le crédit reste libellé dans sa devise ; aucune compensation USD/CDF implicite. Toute utilisation, correction ou restitution est auditée. |
| D6 — Numérotation des reçus | A | Séquence par tenant et par exercice financier, avec unicité et allocation transactionnelle. |
| D7 — Publication/correction des bulletins | C | Direction et responsables académiques explicitement habilités. Publication et correction peuvent avoir des permissions distinctes. Contrôle serveur et audit obligatoires. |
| D8 — Consultation des versions remplacées | B | Direction et responsables académiques habilités uniquement ; les versions restent conservées et identifiées comme remplacées. |
| D9 — Révocation d'un bulletin | B | Autorisée uniquement via un contrat dédié : motif obligatoire, autorité, effet sur la visibilité, conservation du snapshot et traitement des décisions aval explicités. Ne pas implémenter avant ce contrat. |
| D10 — Parent/responsable | OUI | Plusieurs responsables autorisés par élève et plusieurs élèves par responsable. Validation par direction ou agent explicitement habilité. Parent, responsable autorisé et responsable légal sont des notions distinctes. Accès limité aux données explicitement autorisées et vérifiées côté serveur. Historique non destructif. |
| D11 — Migrations | A | Migrations exécutées par un opérateur avant démarrage, avec procédure de sauvegarde, vérification et retour arrière documentée. Pas de migration automatique au démarrage en V1. |
| D12 — Parcours frontend prioritaire | A | Configuration scolaire et calendrier en premier ; les parcours dépendants suivent après validation de ce socle. |

## Précisions de modélisation obligatoires

1. Le tenant représente l'espace SaaS ; le profil de l'établissement est une donnée métier distincte. Ne pas créer un second tenant pour représenter l'école.
2. Les politiques doivent rester dans leurs bounded contexts : politique académique, politique de facturation, workflow et documents. Éviter un agrégat monolithique de paramètres génériques.
3. Toute politique qui affecte un calcul ou une décision est versionnée, datée (date d'effet) et liée à l'opération qui l'a utilisée.
4. Une nouvelle version de politique ne modifie pas les résultats, obligations ou reçus historiques.
5. Les valeurs officielles (matières, maxima, coefficients, seuils, passages, mentions, calendriers réglementaires) ne sont jamais inventées par EduNova. Elles sont configurées par l'établissement après vérification des règles applicables.
6. Les configurations de test utilisent des données synthétiques et ne deviennent pas des valeurs par défaut de production.
7. La décision D5 sur le crédit ne permet pas d'écraser un paiement confirmé ni son reçu. Elle complète les règles financières canoniques FIN-COR-01 et FIN-REC-01.
8. Les décisions D7 à D9 ne lèvent pas les réserves documentées dans BUL-TECH-02 à BUL-TECH-06 ; les contrats techniques restent requis avant exposition de ces opérations.

## Ordre d'implémentation autorisé

- Tranche 0 : réconcilier les documents et auditer les contrats/code existants.
- Tranche 1 : configuration scolaire versionnée et calendrier tenant-scoped.
- Tranche 2 : profils et politiques académiques configurables, sans valeurs réglementaires inventées.
- Tranche 3 : permissions métier explicites et workflows configurables.
- Tranches suivantes : identification/doublons, parent-responsable, crédit financier et documents, chacune avec contrat, tests et migration isolée.

Une décision ratifiée n'autorise pas une migration de base persistante. Toute migration doit être testée sur une base temporaire et rester soumise au processus de revue GitHub.
