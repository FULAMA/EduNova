# Registre des décisions métier — EduNova

> **Statut :** référence métier destinée à l'équipe EduNova et à Codex.
> **Source :** décisions validées dans la conversation.
> **Périmètre :** décisions 1 à 44 validées ; décision suivante en attente.

## 1. Instructions impératives pour Codex

1. Lire ce document avant toute tâche qui concerne les règles métier consignées.
2. Considérer uniquement les décisions marquées `VALIDÉE` comme adoptées.
3. Ne jamais considérer une recommandation ou une option en attente comme une décision validée.
4. En cas de contradiction avec le code, inspecter et signaler l'écart avant toute modification.
5. Ne pas effectuer de refactorisation, migration ou modification de données implicitement.
6. Préserver l'architecture existante, les tests, la traçabilité et l'isolation multi-tenant.
7. Une décision enregistrée ne constitue pas, à elle seule, une autorisation d'implémenter.
8. Toute implémentation nécessite une demande explicite et le respect du processus de validation du projet.
9. Ne jamais supprimer l'historique d'une décision modifiée : conserver son motif, son statut et sa nouvelle version.
10. Ce registre est une référence documentaire, pas une source de vérité technique qui remplacerait les tests, les migrations ou le code.

## 2. Décisions métier validées

### Décision 1 — Seuil de réussite par matière
**Statut : VALIDÉE**

Le seuil est configurable par établissement. Une matière est réussie si la moyenne atteint le seuil configuré. La valeur numérique applicable au pilote reste à définir.

### Décision 2 — Politique académique à l'ouverture d'une période
**Statut : VALIDÉE**

La politique applicable est fixée à l'ouverture de la période. Sa version est conservée pour chaque calcul. Toute modification en cours de période suit une procédure explicite et traçable.

### Décision 3 — Correction d'un dossier académique validé
**Statut : VALIDÉE**

Toute correction crée une nouvelle version. L'ancienne version est conservée avec auteur, horodatage et motif obligatoire. L'accès est limité aux personnes autorisées.

### Décision 4 — Crédits académiques
**Statut : VALIDÉE**

Les crédits sont exclus du périmètre initial tant que leur utilité et les règles officielles applicables ne sont pas clarifiées. Ils n'influencent pas les notes ni les décisions du pilote.

### Décision 5 — Formule de moyenne générale
**Statut : VALIDÉE**

La formule est configurable par établissement, versionnée et traçable pour chaque calcul. Les résultats historiques ne doivent jamais être réinterprétés silencieusement.

### Décision 6 — Notes manquantes et zéros
**Statut : VALIDÉE**

Une note manquante est distincte d'un zéro. Distinguer les notes en attente, les évaluations non passées ou absences et les notes saisies. Les résultats provisoires sont identifiés comme tels. Les résultats ne deviennent officiels que lorsque les conditions de complétude prévues sont remplies.

### Décision 7 — Validation et publication des résultats
**Statut : VALIDÉE**

Le workflow est configurable par établissement : rôles, étapes et validations. Les actions sont tracées.

### Décision 8 — Correction après publication officielle
**Statut : VALIDÉE**

La procédure est configurable, mais conserve l'historique, le motif, les autorisations, les validations et les notifications pertinentes. La version officielle courante doit être identifiable.

### Décision 9 — Modification d'une politique en cours de période
**Statut : VALIDÉE**

Le traitement dépend de la nature de la modification, de l'autorité, de la date d'effet, du périmètre et de la traçabilité. Aucun recalcul rétroactif automatique. Tout recalcul exceptionnel exige une autorisation et une trace complète.

### Décision 10 — Année scolaire et périodes
**Statut : VALIDÉE**

Utiliser des modèles organisationnels officiels avec adaptations autorisées, documentées et traçables. Distinguer année scolaire, périodes académiques et périodes d'évaluation. Ne pas inventer les modèles officiels avant vérification.

### Décision 11 — Coefficients des matières
**Statut : VALIDÉE**

Les coefficients s'appuient sur les modèles officiels applicables à l'organisation scolaire, au niveau et à l'option. Les adaptations autorisées sont versionnées et traçables. Vérifier les références officielles avant de configurer les valeurs réelles. Chaque calcul conserve la version des coefficients utilisée.

### Décision 12 — Transferts d'élèves
**Statut : VALIDÉE**

Les procédures sont configurables selon le type de transfert : changement interne de classe ou transfert interétablissements. La provenance et l'historique sont obligatoires. Les anciens résultats ne sont pas recalculés automatiquement selon les règles du nouvel établissement. Toute reconnaissance ou intégration suit une procédure autorisée.

### Décision 13 — Permissions par rôle
**Statut : VALIDÉE**

Les permissions sont configurables par établissement et rôle, avec socle de sécurité obligatoire, contrôle de portée et isolation des tenants. L'élève consulte ses propres résultats ; le parent ceux des enfants officiellement associés ; l'enseignant ses classes et matières affectées ; la direction les données relevant de ses responsabilités. Les accès sensibles et changements de permission sont tracés.

### Décision 14 — Comptes multi-rôles
**Statut : VALIDÉE**

Un compte n'a qu'un rôle ou contexte actif à la fois. Le changement de contexte est contrôlé. Les permissions dépendent du contexte actif et ne se cumulent pas par fusion. Les actions sensibles et changements de contexte sont tracés.

### Décision 15 — Absences aux évaluations
**Statut : VALIDÉE**

Le traitement des absences est configurable selon la réglementation. Distinguer absence justifiée, non justifiée et justification en attente. Toute conséquence, comme un rattrapage ou une décision administrative, doit être autorisée et tracée. Une absence ne devient pas automatiquement un zéro dans tous les cas.

### Décision 16 — Consultation des bulletins
**Statut : VALIDÉE**

Les élèves et parents ne consultent les bulletins qu'après publication officielle. Les résultats provisoires restent réservés au personnel autorisé. Les enseignants et la direction accèdent uniquement aux données relevant de leur périmètre.

### Décision 17 — Transfert interétablissements
**Statut : VALIDÉE**

Importer le dossier de l'élève sans modifier ses résultats d'origine. La reconnaissance des résultats suit une procédure autorisée et conserve la provenance. Aucun remplacement silencieux des résultats sources.

### Décision 18 — Contestation d'une note
**Statut : VALIDÉE**

Prévoir une procédure formelle de réclamation, une révision autorisée et une décision motivée. Toute correction approuvée est versionnée. Une réclamation ne modifie jamais automatiquement une note.

### Décision 19 — Journal financier
**Statut : VALIDÉE**

Les transactions individuelles sont traçables. Les paiements partiels sont pris en charge. Les corrections se font par annulation ou régularisation sans effacer la transaction d'origine. USD et CDF restent séparés ; ils ne sont pas additionnés directement. Toute conversion est explicite et traçable.

### Décision 20 — Frais scolaires
**Statut : VALIDÉE**

Le barème est configurable et versionné. Les obligations sont individualisées par élève. Les réductions et exonérations nécessitent autorisation, motif et historique. La modification du barème ne change pas silencieusement les obligations déjà établies.

### Décision 21 — Responsabilités financières
**Statut : VALIDÉE**

Les responsabilités sont configurables. La confirmation des paiements est contrôlée ; les annulations nécessitent une autorisation distincte. Les opérations sont auditées, avec permissions explicites et portée limitée à l'établissement.

### Décision 22 — Échéanciers et impayés
**Statut : VALIDÉE**

Les échéances sont configurables. Les arriérés sont calculés à partir des obligations et paiements confirmés. Les rappels sont suivis. Aucune pénalité ou sanction automatique non autorisée. Un paiement saisi mais non confirmé ne constitue pas un reçu définitif.

### Décision 23 — Tableau de bord promoteur
**Statut : VALIDÉE**

Afficher les frais attendus, paiements confirmés, soldes dus, arriérés, reçus par période et ventilation par classe, avec USD et CDF séparés. Les indicateurs doivent se réconcilier avec les transactions et respecter les permissions.

### Décision 24 — Notifications
**Statut : VALIDÉE**

Les notifications sont configurables par événement, rôle, destinataire et canal. Assurer traçabilité, préférences et confidentialité. Distinguer échec d'envoi et livraison lorsque l'information est disponible. Ne jamais transmettre de données sensibles à un destinataire non autorisé.

### Décision 25 — Mode hors ligne
**Statut : VALIDÉE**

Le mode hors ligne est limité aux fonctions autorisées. La synchronisation est contrôlée, avec détection des conflits et doublons, protection locale et validation serveur des opérations sensibles. Une action locale en attente n'est pas confirmée par le serveur. Aucun écrasement silencieux. L'interface distingue hors ligne, en attente, synchronisé et erreur.

### Décision 26 — Cycle de vie des comptes
**Statut : VALIDÉE**

La création ou invitation, l'activation, la suspension et la désactivation sont contrôlées. Les changements d'accès sont revus et audités ; l'historique est conservé. Les opérations sont réservées au personnel autorisé. L'association à un établissement et les rôles sont contrôlés.

### Décision 27 — Authentification
**Statut : VALIDÉE**

Les mesures sont proportionnées au risque : mots de passe protégés, limitation des tentatives, gestion des sessions, MFA pour les comptes privilégiés et vérification supplémentaire pour les actions sensibles.

### Décision 28 — Incidents de sécurité
**Statut : VALIDÉE**

Prévoir un processus structuré : détection, classification de gravité, confinement, révocation des accès compromis, préservation des preuves, désignation des responsables, restauration contrôlée et suivi.

### Décision 29 — Sauvegardes
**Statut : VALIDÉE**

Les sauvegardes sont protégées et séparées. Leur intégrité est vérifiée et les restaurations sont testées. RPO et RTO sont adaptés à la criticité.

### Décision 30 — Journaux d'audit
**Statut : VALIDÉE**

Les opérations sensibles génèrent des journaux protégés comprenant le contexte établissement, acteur, action, cible, horodatage et résultat. L'accès et la durée de conservation sont contrôlés. Aucun secret ne doit être écrit dans les journaux.

### Décision 31 — Cycle de vie des données
**Statut : VALIDÉE**

Définir par catégorie les finalités, la minimisation, les durées de conservation, l'archivage contrôlé et la suppression ou anonymisation lorsqu'elle est permise, en respectant les obligations légales de conservation.

### Décision 32 — Isolation multi-tenant
**Statut : VALIDÉE**

L'isolation s'applique à toutes les couches pertinentes : contexte et autorisation côté serveur, requêtes limitées au tenant, protections au niveau de la base de données et tests négatifs inter-tenants. Cela inclut tâches en arrière-plan, exports, rapports et opérations d'administration.

### Décision 33 — Gestion des erreurs
**Statut : VALIDÉE**

Utiliser une gestion uniforme et classifiée : messages adaptés, journaux techniques protégés, identifiants de corrélation et confirmation de réussite uniquement après confirmation réelle. Distinguer en attente, confirmé et échoué ; éviter les doublons lors des nouvelles tentatives.

### Décision 34 — Stratégie de tests
**Statut : VALIDÉE**

Tests à plusieurs niveaux selon le risque : unitaires, intégration, bout en bout, sécurité, isolation multi-tenant et non-régression. Les fonctions critiques ont des critères d'acceptation renforcés. Une livraison est bloquée si les contrôles obligatoires échouent.

### Décision 35 — Déploiement et retour arrière
**Statut : VALIDÉE**

Déploiement contrôlé avec validation préalable, sauvegardes proportionnées au risque, déploiement progressif si possible, supervision et procédure de retour arrière. Les migrations préservent les données ; retour arrière du code et des données sont traités séparément.

### Décision 36 — Environnements
**Statut : VALIDÉE**

Séparer strictement développement, test ou préproduction et production. Utiliser des données de test synthétiques ou anonymisées, isoler secrets et accès, limiter l'accès à la production et contrôler la promotion des versions.

### Décision 37 — Dépendances
**Statut : VALIDÉE**

Inventorier les dépendances directes et transitives, verrouiller les versions, scanner vulnérabilités et licences, limiter les dépendances inutiles et prioriser les mises à jour selon le risque avec tests préalables.

### Décision 38 — Protection de la vie privée
**Statut : VALIDÉE**

Documenter minimisation et finalités, vérifier les obligations légales en RDC et pour les transferts concernés, encadrer les sous-traitants, prévoir les demandes des personnes concernées et la gestion des violations de données.

### Décision 39 — Exports
**Statut : VALIDÉE**

Les exports sont gouvernés par le rôle, le contexte actif, l'établissement et la finalité. Les champs et volumes sont contrôlés ; les fichiers sensibles sont protégés, leur durée d'accès est limitée si possible et les exports sensibles sont tracés. L'isolation multi-tenant est maintenue.

### Décision 40 — Performance
**Statut : VALIDÉE**

Mesurer les parcours critiques et les faire évoluer progressivement. Utiliser supervision, tests de charge et optimisations fondées sur des mesures, sans compromettre la sécurité ni l'isolation des tenants.

### Décision 41 — Observabilité
**Statut : VALIDÉE**

Mettre en place journaux, métriques, traces pertinentes, identifiants de corrélation et alertes ; superviser les parcours critiques, protéger les données et prévoir la réponse aux incidents.

### Décision 42 — Gouvernance des évolutions produit
**Statut : VALIDÉE**

Prioriser les changements selon valeur métier, impact, risque et coût de maintenance. Privilégier les fonctions communes et la configuration légitime. Toute évolution doit disposer d'une spécification, de tests, d'une version et d'une communication adaptées.

### Décision 43 — Responsabilité de la numérisation initiale
**Statut : VALIDÉE — choix A**

L'équipe EduNova prend en charge la numérisation avec la participation de l'école.
- EduNova organise la collecte, classe les documents, saisit les données, contrôle leur cohérence et documente les anomalies.
- L'école fournit les documents autorisés, clarifie les informations et valide les données relevant de sa responsabilité.
- Les données ambiguës ou contradictoires restent en attente ; aucune supposition n'est autorisée.
- La source, le traitement, les anomalies et la validation de chaque lot sont traçables.
- L'accès aux documents et données est réservé aux personnes autorisées et limité à l'établissement concerné.

### Décision 44 — Priorité de numérisation
**Statut : VALIDÉE — choix A**

Priorité à l'année scolaire en cours, puis traitement progressif des archives selon les besoins.
- Priorité aux élèves actifs, au personnel actuel, aux classes, aux matières, aux affectations et aux données nécessaires au fonctionnement quotidien.
- Traiter ensuite les résultats et les données financières nécessaires à la continuité des opérations.
- Numériser les archives historiques progressivement selon les besoins, les demandes autorisées et les obligations de conservation.
- Aucune donnée ne devient officiellement exploitable avant les contrôles requis.
- Le traitement des archives ne doit pas retarder inutilement le lancement des fonctions prioritaires.

## 3. Décision suivante en attente

### Décision 45 — Identification des personnes et prévention des doublons
**Statut : EN ATTENTE — aucune option validée**

- **Option A :** attribuer un identifiant interne EduNova à chaque dossier, conserver les matricules existants comme références et signaler les correspondances possibles pour vérification humaine avant toute fusion.
- **Option B :** exiger un matricule existant ou attribué par l'école avant l'enregistrement définitif.
- **Option C :** utiliser le nom et la date de naissance comme critères principaux, avec vérification manuelle des dossiers potentiellement identiques.

**Recommandation non validée :** option A. Elle permet de traiter les archives incomplètes sans inventer de matricule officiel et limite les fusions erronées.

## 4. Point de cohérence de numérotation

Une décision sur l'activation progressive des fonctionnalités (*feature flags*) avait été proposée sous le numéro 43 avant que la conversation passe à la numérisation. Aucun choix n'avait été validé pour cette décision. Les décisions 43 et 44 ci-dessus correspondent aux choix de numérisation ensuite explicitement validés.

La question des feature flags reste à reprendre et à renuméroter proprement lors d'une révision du registre. Ne pas la considérer comme validée.

## 5. État documentaire

Ce fichier consigne les décisions de conversation. Son existence n'autorise aucune modification implicite du code, des migrations ou des bases de données. Toute implémentation est une tâche distincte, à demander et valider explicitement.

## 6. Réconciliation canonique des bulletins V1

Les identifiants canoniques suivants complètent les décisions historiques sans les supprimer ni les renuméroter.

### BUL-CAL-01 — Périodes configurables par profil académique
**Statut : VALIDÉE**

Les périodes scolaires sont définies par un profil académique versionné, applicable au niveau, au programme et à l'option lorsque nécessaire.

### BUL-PUB-01 — Délibération persistée avant publication officielle
**Statut : VALIDÉE**

Toute publication officielle exige une délibération persistée et versionnée, liée au dossier académique, à sa version, à la période, au profil et à la politique utilisés.

### BUL-COR-01 — Correction versionnée d'un bulletin émis
**Statut : VALIDÉE**

Toute correction crée une nouvelle version. L'ancienne est conservée et reçoit `SUPERSEDED` lorsqu'elle est remplacée. Son snapshot reste immuable.

### BUL-CALC-01 — Politique de calcul et arrondi
**Statut : VALIDÉE AVEC RÉSERVE RÉGLEMENTAIRE**

Les calculs utilisent une politique versionnée et un mode d'arrondi explicite. Deux décimales sont le défaut technique proposé, sous réserve de conformité réglementaire.

### BUL-DOC-01 — PDF issu d'un snapshot immuable
**Statut : VALIDÉE**

Le bulletin officiel est un PDF rendu depuis un snapshot immuable, avec renderer injectable.

### BUL-PROF-01 — Profils académiques versionnés
**Statut : VALIDÉE**

Les profils sont versionnés par niveau, programme et option si nécessaire. Les valeurs officielles ne sont pas déduites d'un exemple visuel.

### BUL-SCOPE-01 — Périmètre V1 multi-niveaux
**Statut : VALIDÉE**

La V1 couvre le primaire, le secondaire inférieur et les humanités. Les règles propres à chaque niveau restent à confirmer.

### BUL-REG-01 — Règles réglementaires propres aux niveaux
**Statut : EN ATTENTE DE CONFIRMATION**

Programmes, matières, maxima, coefficients, périodes, repêchage, décisions de passage, mentions, signatures et mentions légales restent ouverts.

### BUL-TECH-01 — Choix techniques de publication
**Statut : EN ATTENTE DE DÉCISION TECHNIQUE**

Stockage du PDF, rétention, identifiant légal, rôles d'émission/téléchargement/révocation et stratégie de révocation restent à décider.

## 7. Clarifications documentaires Tranche 0.1

Cette section précise les décisions canoniques sans modifier l'historique numérique ni créer de règle réglementaire.

- `BUL-PUB-01` correspond au choix historique D4-A : aucune publication officielle sans délibération persistée et versionnée.
- `BUL-DOC-01` correspond au choix historique D5-B : le PDF est rendu depuis un snapshot immuable. Le mode de stockage reste `BUL-TECH-01`.
- `BUL-COR-01` correspond au choix historique D6-A pour le remplacement : une nouvelle version est créée et l'ancienne reçoit `SUPERSEDED`.
- Le remplacement `SUPERSEDED` et la révocation sont deux opérations distinctes. La révocation, ses motifs, ses effets et ses autorisations restent ouverts sous `BUL-TECH-01`.
- `BUL-CALC-01` retient deux décimales comme défaut technique, sans les déclarer conformes à une réglementation non vérifiée.
## Décisions financières canoniques V1

Les décisions suivantes complètent les options historiques D8, D11 et D12 sans les effacer :

| Identifiant | Décision | Statut |
|---|---|---|
| `FIN-ROLE-01` | La finance est accessible à la direction et aux rôles `ACCOUNTANT` ou `CASHIER` explicitement affectés au tenant ; le contrôle est côté serveur. | VALIDÉE |
| `FIN-COR-01` | Un paiement confirmé n'est jamais supprimé ni écrasé. Une correction est une contre-écriture traçable, liée au paiement original, avec motif, auteur, date, unicité et contrôle de concurrence. | VALIDÉE |
| `FIN-REC-01` | Le reçu reste consultable et traçable. Il est générable/téléchargeable en PDF ; une contre-écriture ne supprime pas le reçu original. Stockage, rétention et conformité légale restent à confirmer. | VALIDÉE AVEC RÉSERVES |

## 9. Questions ouvertes du cycle ReportCard

## 10. Propositions Parent-enfant - a confirmer

Cette section documente des propositions de conception. Elle ne modifie pas les decisions validees et n'autorise aucune route ou migration.

### PAR-REL-01 - Cardinalite Parent-enfant

**Statut : PROPOSED - CONFIRMATION METIER REQUISE**

Proposition : un parent ou responsable peut etre associe a plusieurs eleves et un eleve peut avoir plusieurs responsables autorises. Les cardinalites exactes, la notion de responsable legal et les cas de garde partagee restent a confirmer.

### PAR-REL-02 - Validation et gestion du rattachement

**Statut : PROPOSED - BLOCKED**

Proposition : la creation, la validation, la suspension et la fin d'un rattachement sont des actions serveur realisees par une personne habilitee. Les roles exacts, les preuves requises, les motifs et les transitions de statut ne sont pas determines.

### PAR-REL-03 - Historique non destructif

**Statut : PROPOSED - CONFIRMATION TECHNIQUE ET METIER REQUISE**

Proposition : conserver l'auteur, la date, le motif et les transitions d'une association sans supprimer l'historique. La retention, la consultation de l'historique et la strategie de reactivation restent ouvertes.

### PAR-REL-04 - Acces Parent aux donnees scolaires

**Statut : PROPOSED - BLOCKED**

Proposition : apres validation du rattachement, le parent pourrait consulter les bulletins officiels, les resultats et les presences de ses enfants, sous reserve de permissions distinctes par categorie. Les roles autorises et la politique de visibilite restent a confirmer.

### PAR-REL-05 - Separation avec StudentUserLink

**Statut : TECHNIQUEMENT CONFIRME**

`StudentUserLink` reste reserve au lien du compte du portail eleve. Une association Parent-enfant doit etre un modele distinct : les contraintes actuelles ne permettent pas de representer les cardinalites proposees.

### Revision proposee du 2026-10-22

Les propositions ci-dessous constituent la version courante a examiner. Les blocs precedents sont conserves comme historique de redaction et ne valent pas approbation definitive.

| Identifiant | Proposition actualisee | Statut |
|---|---|---|
| `PAR-REL-01` | Plusieurs parents ou responsables autorises peuvent etre associes a un meme eleve, et un parent peut etre associe a plusieurs eleves. L'association reste tenant-scoped. La definition du responsable legal et les cas de garde partagee restent a confirmer. | `PROPOSED - CONFIRMATION METIER REQUISE` |
| `PAR-REL-02` | La creation et la validation d'un rattachement sont reservees a la direction ou a un agent disposant d'une permission explicite. Le role `PARENT` seul n'accorde pas ce droit. | `PROPOSED - BLOCKED` |
| `PAR-REL-03` | La verification suit la procedure de l'etablissement. Cette proposition n'impose aucune preuve documentaire specifique ; les preuves, motifs, acteurs et conditions de validation restent a definir par decision metier. | `PROPOSED - BLOCKED` |
| `PAR-REL-04` | Le cycle de vie propose est `PENDING`, `ACTIVE`, `REVOKED`. Apres revocation, un nouveau rattachement est cree pour un nouveau lien ; l'ancien reste conserve dans l'historique. Les modalites de retablissement et de conservation restent ouvertes. | `PROPOSED - BLOCKED` |
| `PAR-REL-06` | Un parent peut consulter les bulletins officiels, resultats et presences de l'enfant uniquement si le serveur verifie l'association active, le tenant et les permissions applicables. Les donnees provisoires, remplacees ou hors perimetre restent exclues. | `PROPOSED - BLOCKED` |

#### Compatibilite et limites

- Ces propositions sont compatibles avec l'isolation obligatoire par `tenant_id` et avec la regle existante de consultation des seuls bulletins officiels pour les profils autorises.
- Elles ne modifient pas le contrat actuel de `StudentUserLink`. Ce modele reste un lien compte-eleve ; ses contraintes d'unicite ne peuvent pas porter les cardinalites parent-enfant proposees.
- Le role `PARENT` ne suffit pas a lui seul pour autoriser une association ou une consultation : les controles doivent rester effectues cote serveur dans le contexte du tenant.
- L'historique d'audit est propose comme non modifiable, mais sa duree de conservation, ses modalites de consultation et sa politique de retention restent a arbitrer.
- Aucune route, migration, permission ou persistance n'est activee par cette mise a jour documentaire.

#### Confirmations necessaires avant implementation

1. Definition metier de parent, responsable autorise et responsable legal.
2. Roles ou permissions exacts de la direction et des agents habilites.
3. Procedure de verification de l'etablissement et informations a conserver.
4. Conditions de passage `PENDING -> ACTIVE`, de revocation et de creation d'un nouveau rattachement.
5. Perimetre exact des bulletins, resultats et presences consultables.
6. Duree de conservation et acces a l'historique d'audit.

Cette section est additive. Elle ne remplace pas les décisions historiques et ne transforme pas les options en décisions validées.

### BUL-TECH-02 - Autorisations de publication et correction

**Statut : EN ATTENTE DE DECISION PRODUIT**

L'implementation actuelle reserve la publication et la correction au role `ADMIN`, conforme aux controles techniques existants. Il reste a confirmer si un role de direction ou un role academique habilite doit etre autorise, et si les roles de publication et de correction doivent etre distincts. Ce choix determine les permissions backend, les tests multi-tenant et l'audit des acteurs.

### BUL-TECH-03 - Consultation des versions remplacees

**Statut : EN ATTENTE DE DECISION PRODUIT**

Les versions `SUPERSEDED` sont conservees pour l'historique mais ne sont pas exposees dans la liste et le detail du portail eleve. Il reste a decider quels roles peuvent les consulter, dans quelles circonstances et avec quelles mentions d'historique.

### BUL-TECH-04 - Revocation d'un bulletin emis

**Statut : EN ATTENTE DE DECISION PRODUIT**

La revocation reste distincte du remplacement. Il faut definir les roles autorises, les motifs obligatoires, l'effet sur la visibilite, la conservation du snapshot et le traitement d'une deliberation ou d'une promotion deja utilisee. Aucune route de revocation n'est consideree comme validee.

### BUL-TECH-05 - Stockage et retention du PDF officiel

**Statut : EN ATTENTE DE DECISION TECHNIQUE ET REGLEMENTAIRE**

Le PDF est actuellement rendu a la demande depuis le snapshot immuable. Il reste a arbitrer entre ce rendu a la demande et une archive persistante, ainsi que la retention, les permissions du stockage, l'integrite, la sauvegarde et la suppression eventuelle.

### BUL-TECH-06 - Audit des emissions et telechargements

**Statut : EN ATTENTE DE CONTRAT D'AUDIT**

Il faut definir les evenements obligatoires pour la preparation, l'emission, la correction, la revocation et le telechargement, les donnees minimales conservees, les consommateurs et la retention. L'implementation actuelle ne presume pas l'existence d'un evenement ReportCard ou d'un sink d'audit specifique sans contrat etabli.

