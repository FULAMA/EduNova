# EduNova - Preparation du modele DDD Parent-enfant

## Statut

Audit realise avec documentation de propositions. Aucun modele Parent-enfant, endpoint ou migration n'a ete active.

## Faits verifies

- `StudentUserLink` relie un compte a un eleve dans un tenant et conserve `created_by` et `created_at`.
- La migration `030_student_user_links` impose une cle primaire `(tenant_id, user_id)` et une unicite `(tenant_id, student_id)`.
- Ce lien est utilise par le portail eleve et ne peut pas representer plusieurs responsables pour un eleve ou plusieurs enfants pour un parent.
- `StudentAssignment` relie un eleve a une classe et une annee scolaire ; il ne relie pas un professeur a une ressource pedagogique.
- Les memberships portent un role et un tenant, mais ne constituent pas une preuve de rattachement familial ou d'affectation pedagogique.
- Le contexte tenant est deduit du JWT et verifie par le membership serveur.

## Modele conceptuel propose

Une future entite `ParentStudentAssociation` pourrait contenir `id`, `tenant_id`, `parent_user_id`, `student_id`, un statut, les dates, les auteurs, un motif et l'historique des transitions.

Cardinalites proposees, non validees : plusieurs responsables par eleve et plusieurs eleves par responsable.

## Invariants proposes

- Les deux parties appartiennent au meme tenant.
- Les utilisateurs et eleves references existent.
- Un rattachement actif a ete valide par une identite habilitee.
- Un rattachement termine ou revoque ne donne plus acces.
- Les doublons actifs sont refuses.
- L'historique n'est jamais ecrase.

Les transitions, les preuves, les roles habilites et la reactivation sont `BLOCKED - CONFIRMATION METIER REQUISE`.

## Matrice d'acces proposee

| Donnee | Parent rattache et valide | Eleve | Personnel autorise |
|---|---|---|---|
| Bulletin officiel | Selon permission a confirmer | Oui, propre dossier | Selon perimetre |
| Resultats | Selon permission a confirmer | Oui, propre dossier | Selon perimetre |
| Presences | Selon permission a confirmer | Oui, propre dossier | Selon perimetre |

Chaque requete devra verifier le tenant et le rattachement cote serveur. Un `student_id` fourni par le client ne sera jamais une preuve d'autorisation.

## Schema futur, non execute

Une migration future pourrait ajouter une table d'association avec une cle primaire tenant-scoped, des cles etrangeres composites, un index sur les rattachements actifs et une table d'historique append-only. Le schema exact depend des decisions de statut, de preuve, de retention et de reactivation.

## Decisions a confirmer

1. Cardinalites Parent-enfant.
2. Roles autorises pour creer, valider, suspendre et terminer.
3. Preuves requises et validation.
4. Statuts, transitions, reactivation et revocation.
5. Visibilite distincte des bulletins, resultats et presences.
6. Retention et acces a l'historique.

## Tests a prevoir apres arbitrage

- association valide dans un tenant ;
- doublon actif refuse ;
- compte ou eleve d'un autre tenant refuse ;
- acces retire apres terminaison ou revocation ;
- listes et details soumis au meme controle ;
- absence de fuite dans les erreurs et reponses ;
- migration sur base temporaire et preservation des donnees existantes.

## Verification

- Fichiers applicatifs modifies : aucun.
- Migrations executees : aucune.
- Tests executes : aucun, car les contrats metier restent ouverts.
- Bases permanentes : non ouvertes en ecriture.
- Serveurs : non redemarres.
