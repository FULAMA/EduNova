# EDUNOVA --- Règles métier consolidées et propositions d'évolution

**Version :** 1.0\
**Date :** 21 novembre 2026\
**Statut :** Proposition de règles à examiner et à ratifier\
**Périmètre :** ERP scolaire SaaS multi-établissements --- RDC,
extensible à l'international

------------------------------------------------------------------------

## 1. Objet du document

Ce document transforme les recommandations issues du benchmark d'ERP
scolaires nationaux, africains et internationaux en règles métier
structurées pour EduNova.

Il vise à : - formaliser les invariants métier que le système doit
garantir ; - harmoniser les cycles de vie scolaires, académiques,
financiers et administratifs ; - renforcer la cohérence entre les
modules ; - préparer l'interopérabilité avec les systèmes éducatifs et
financiers externes ; - encadrer l'évolution fonctionnelle sans
introduire de complexité inutile.

**Important :** les règles marquées « Proposition » ne sont pas réputées
ratifiées. Elles doivent être confrontées au registre de décisions
métier existant, puis approuvées avant implémentation. En cas de
contradiction, une décision métier déjà ratifiée prévaut jusqu'à
arbitrage explicite.

## 2. Principes directeurs

### RB-GEN-001 --- Source de vérité métier

Chaque donnée métier doit avoir un module propriétaire clairement
identifié. Les autres modules consomment cette donnée par contrat ou
événement, sans créer de copies concurrentes modifiables.

### RB-GEN-002 --- Intégrité avant automatisation

Toute automatisation doit préserver les contraintes d'intégrité, les
autorisations, la traçabilité et la possibilité de reprise contrôlée.

### RB-GEN-003 --- Historisation des opérations sensibles

Toute opération modifiant une donnée officielle ou financière doit
conserver son auteur, son horodatage, son motif, son état précédent et
son nouvel état, selon les exigences de conservation applicables.

### RB-GEN-004 --- Séparation des responsabilités

Une même personne ne doit pas pouvoir initier, approuver et contrôler
seule une opération sensible lorsque le niveau de risque exige une
séparation des tâches.

### RB-GEN-005 --- Paramétrage explicite

Les règles variables selon l'établissement, le niveau d'enseignement,
l'année scolaire, le pays ou la devise doivent être configurables et
versionnées. Les valeurs par défaut ne doivent jamais masquer une
décision métier.

### RB-GEN-006 --- Pas de suppression destructive des données officielles

Les dossiers scolaires, résultats validés, paiements confirmés, reçus et
écritures comptables ne doivent pas être effacés pour corriger une
erreur. La correction doit passer par une opération compensatoire, une
annulation autorisée ou une nouvelle version traçable.

### RB-GEN-007 --- Automatisation explicable

Toute action automatique doit pouvoir être expliquée : déclencheur,
règle appliquée, données utilisées, résultat et éventuelle intervention
humaine.

### RB-GEN-008 --- Cloisonnement multi-tenant

Toute donnée appartenant à un établissement doit être isolée par tenant.
Toute lecture, écriture, recherche, exportation, tâche asynchrone et
opération administrative doit appliquer le contexte du tenant et
vérifier les autorisations correspondantes.

## 3. Gestion des établissements et du SaaS

### RB-TEN-001 --- Isolation stricte des établissements

Un utilisateur ne peut accéder qu'aux établissements auxquels il est
explicitement rattaché et pour lesquels son rôle lui accorde une
autorisation active.

### RB-TEN-002 --- Contexte tenant obligatoire

Toute opération métier portant sur une ressource scolaire doit être
exécutée dans un contexte tenant explicite. L'identifiant d'une
ressource ne suffit pas à autoriser son accès.

### RB-TEN-003 --- Unicité contextualisée

Les identifiants métier tels que matricule, numéro de reçu ou code de
classe doivent être uniques dans le périmètre défini par la politique
métier : établissement, année scolaire ou autre portée explicitement
documentée.

### RB-TEN-004 --- Configuration propre à chaque établissement

Chaque établissement peut configurer ses niveaux, classes, options,
périodes, matières, barèmes, devises, calendriers et circuits de
validation dans les limites autorisées par le référentiel national
applicable.

### RB-TEN-005 --- Évolution de configuration versionnée

Une modification de configuration ne doit pas altérer rétroactivement
les résultats ou documents officiels déjà validés. Les opérations
historiques doivent conserver la version de configuration qui leur était
applicable.

### RB-TEN-006 --- Suspension d'un établissement

La suspension d'un tenant bloque les nouvelles opérations selon la
politique contractuelle, sans supprimer les archives, preuves de
paiement ou documents officiels.

## 4. Identités, utilisateurs et autorisations

### RB-IAM-001 --- Identité unique

Un compte utilisateur représente une identité authentifiée. Ses rôles et
rattachements peuvent varier selon l'établissement, sans créer de
privilèges implicites.

### RB-IAM-002 --- Autorisation par action et périmètre

L'autorisation doit être évaluée selon l'utilisateur, le rôle, l'action,
la ressource, le tenant et, si nécessaire, la classe ou le groupe
pédagogique concerné.

### RB-IAM-003 --- Principe du moindre privilège

Un utilisateur ne reçoit que les permissions nécessaires à ses
responsabilités. Une permission financière ne doit pas être utilisée
comme substitut à une permission de consultation scolaire.

### RB-IAM-004 --- Séparation des domaines de permission

Les permissions relatives aux élèves, à la pédagogie, aux finances, aux
ressources humaines, à la configuration et à l'administration technique
doivent être distinctes.

### RB-IAM-005 --- Accès des enseignants

Un enseignant ne peut consulter ou modifier que les données pédagogiques
correspondant à ses affectations et aux périodes autorisées. L'accès aux
informations financières des familles n'est pas accordé par défaut.

### RB-IAM-006 --- Accès des parents

Un parent ou tuteur ne peut consulter que les informations des enfants
qui lui sont explicitement rattachés et dont le rattachement a été
vérifié.

### RB-IAM-007 --- Accès des élèves

Un élève ne peut consulter que ses propres informations et les
ressources qui lui sont destinées.

### RB-IAM-008 --- Authentification renforcée

Les opérations à risque élevé --- administration, gestion des rôles,
opérations financières sensibles et accès aux données critiques ---
doivent pouvoir exiger une authentification renforcée.

### RB-IAM-009 --- Révocation immédiate

La désactivation d'un compte, d'une session ou d'un rattachement doit
empêcher les nouveaux accès dans un délai défini et documenté.

### RB-IAM-010 --- Traçabilité des accès sensibles

Les consultations, exports et modifications de données sensibles doivent
être journalisés selon une politique proportionnée, sans exposer les
secrets ou données inutiles dans les journaux.

## 5. Cycle de vie de l'élève

### RB-STU-001 --- Préinscription distincte de l'inscription

La préinscription constitue une demande. Elle ne crée pas
automatiquement un statut d'élève régulièrement inscrit.

### RB-STU-002 --- Dossier candidat

Une demande de préinscription doit contenir les informations minimales
exigées par l'établissement et signaler les pièces manquantes.

### RB-STU-003 --- Contrôle des doublons

Avant la création d'un nouveau dossier élève, le système doit rechercher
les correspondances potentielles selon les critères autorisés. Une
correspondance potentielle doit être examinée, et non fusionnée
automatiquement.

### RB-STU-004 --- Admission explicite

L'admission doit résulter d'une décision autorisée et traçable. Une
demande acceptée ne devient pas automatiquement une inscription
définitive si des conditions restent à satisfaire.

### RB-STU-005 --- Inscription sans frais automatiques

La création ou la validation d'une inscription ne doit pas générer
automatiquement des frais, sauf règle explicite, paramétrée, approuvée
et visible par l'établissement et la famille.

### RB-STU-006 --- Affectation scolaire obligatoire

Un élève régulièrement inscrit doit être affecté à une structure
scolaire valide : année scolaire, niveau, classe et, si applicable,
option ou groupe.

### RB-STU-007 --- Cohérence des affectations

Une affectation ne peut référencer une classe inactive, une année
clôturée ou une structure incompatible avec le niveau de l'élève.

### RB-STU-008 --- Historique des affectations

Toute réaffectation, mutation ou correction d'affectation doit conserver
l'historique, le motif, l'auteur et la date d'effet.

### RB-STU-009 --- Transfert entrant

Un transfert entrant doit conserver les informations d'origine
disponibles, faire l'objet d'une vérification et être rattaché à
l'établissement destinataire sans écraser l'historique antérieur.

### RB-STU-010 --- Transfert sortant

Un transfert sortant doit clôturer ou suspendre les rattachements actifs
selon la procédure de l'établissement, sans supprimer le dossier
historique.

### RB-STU-011 --- Promotion contrôlée

La promotion d'un élève doit être fondée sur un résultat officiel validé
et sur les règles de passage applicables. Le statut « ADMITTED » est
requis pour déclencher une promotion automatique ou assistée lorsque
cette règle est applicable au processus.

### RB-STU-012 --- Redoublement et réorientation

Le redoublement, la réorientation et le changement d'option doivent être
des décisions explicites, motivées et historisées.

### RB-STU-013 --- Sortie de l'établissement

La sortie définitive doit préciser son motif, sa date d'effet et son
statut administratif. Elle ne doit pas supprimer les résultats,
paiements ou documents antérieurs.

### RB-STU-014 --- Réactivation

La réactivation d'un ancien dossier doit réutiliser l'identité
historique lorsque cela est certain et créer un nouveau rattachement
scolaire pour la nouvelle période.

## 6. Configuration scolaire et académique

### RB-ACA-001 --- Séparation des configurations

La configuration scolaire (années, niveaux, classes, options,
calendriers et structures) doit être distincte de la configuration
académique (matières, coefficients, évaluations, barèmes et règles de
calcul).

### RB-ACA-002 --- Année scolaire

Une année scolaire possède une date de début, une date de fin, un statut
et des périodes définies. Une seule année ne peut être considérée active
pour un même périmètre si la politique de l'établissement impose
l'unicité.

### RB-ACA-003 --- Configuration préalable

Les cours, évaluations et affectations pédagogiques ne peuvent être
créés que dans une configuration scolaire et académique valide.

### RB-ACA-004 --- Version des barèmes

Les barèmes, coefficients, seuils et règles de calcul doivent être
versionnés et associés à leur période d'application.

### RB-ACA-005 --- Matières et programmes

Une matière ne peut être évaluée dans une classe que si elle est prévue
par la configuration applicable et qu'un enseignant ou responsable est
habilité à intervenir.

### RB-ACA-006 --- Calendrier pédagogique

Les périodes d'enseignement, évaluations, clôtures et délibérations
doivent respecter le calendrier configuré ou faire l'objet d'une
dérogation autorisée.

### RB-ACA-007 --- Pas de modification rétroactive silencieuse

Une modification des matières, coefficients ou barèmes après le début
des évaluations doit être explicitement autorisée, historisée et
analysée quant à son impact sur les résultats existants.

## 7. Présences et vie scolaire

### RB-ATT-001 --- Absence distincte de zéro

Une absence, une donnée non saisie et une note égale à zéro sont trois
états différents. Aucun de ces états ne doit être converti
automatiquement en un autre.

### RB-ATT-002 --- Présence contextualisée

Toute présence doit être rattachée à un élève, une séance ou période,
une classe et une date.

### RB-ATT-003 --- Auteur et correction

Toute saisie ou correction de présence doit identifier son auteur, sa
date et, en cas de correction, son motif.

### RB-ATT-004 --- Justification

Une justification d'absence doit être enregistrée séparément de
l'absence initiale. Son acceptation relève d'un utilisateur habilité.

### RB-ATT-005 --- Notifications

Une notification d'absence à un parent ne doit être envoyée qu'après
validation des règles de destinataire, de rattachement et de
confidentialité.

### RB-ATT-006 --- Synchronisation différée

Les saisies hors ligne doivent être synchronisées avec un identifiant
d'opération unique, une date d'origine et une stratégie de résolution
des conflits.

## 8. Évaluations, notes et délibérations

### RB-GRD-001 --- Évaluation configurée

Une évaluation doit être liée à une matière, une classe, une période, un
barème et un auteur habilité.

### RB-GRD-002 --- Note et résultat officiel distincts

Une note saisie ou calculée n'est pas un résultat officiel tant que le
processus de validation requis n'est pas terminé.

### RB-GRD-003 --- États de résultat

Les résultats doivent suivre des états explicites, par exemple :
brouillon, soumis, vérifié, validé, publié, corrigé ou annulé. Les
transitions autorisées doivent être définies.

### RB-GRD-004 --- Contrôle des valeurs

Une note doit respecter le barème applicable. Toute dérogation doit être
motivée et autorisée.

### RB-GRD-005 --- Absence à l'évaluation

L'absence à une évaluation doit être enregistrée avec un statut dédié et
ne doit pas être assimilée automatiquement à zéro.

### RB-GRD-006 --- Calcul reproductible

Le calcul d'une moyenne ou d'un résultat doit être reproductible à
partir des notes, coefficients, règles et versions de configuration
utilisés.

### RB-GRD-007 --- Validation de période

La clôture d'une période d'évaluation doit vérifier les données
manquantes, incohérences et exceptions avant validation.

### RB-GRD-008 --- Délibération contrôlée

La délibération doit être réservée aux personnes ou instances autorisées
et enregistrer les participants, décisions, motifs et résultats.

### RB-GRD-009 --- Décision de délibération

Les décisions telles que admis, ajourné, redoublement ou réorientation
doivent être représentées par des valeurs métier explicites et
contrôlées.

### RB-GRD-010 --- Promotion après validation

Aucune promotion ne doit être déclenchée sur la base de notes
provisoires ou d'une délibération non validée.

### RB-GRD-011 --- Bulletin versionné

Chaque bulletin publié doit être une version officielle immuable. Une
correction produit une nouvelle version liée à la précédente, avec motif
et approbation.

### RB-GRD-012 --- Publication contrôlée

Un résultat ne peut être visible par les parents ou élèves qu'après
publication par une autorité habilitée.

### RB-GRD-013 --- Rectification après publication

Une rectification après publication doit conserver l'ancienne version,
expliquer le changement et notifier les destinataires concernés lorsque
la politique le prévoit.

### RB-GRD-014 --- Palmarès

Un palmarès doit être calculé à partir des résultats validés et des
règles de classement applicables à la période concernée.

## 9. Gestion financière et frais scolaires

### RB-FIN-001 --- Barème explicite

Les frais scolaires doivent provenir d'un barème approuvé, associé à un
établissement, une année scolaire, un niveau ou une catégorie d'élève et
une devise.

### RB-FIN-002 --- Pas de génération implicite

Aucun frais ne doit être généré uniquement parce qu'un élève a été créé
ou inscrit, sauf règle d'application explicitement approuvée.

### RB-FIN-003 --- Obligation financière traçable

Toute obligation financière doit préciser son origine, son bénéficiaire,
son montant, sa devise, son échéance et son statut.

### RB-FIN-004 --- Échéancier

Un frais peut être réparti en plusieurs échéances si le barème ou une
décision autorisée le permet. Les échéances doivent rester rattachées à
l'obligation d'origine.

### RB-FIN-005 --- Paiement partiel

Un paiement partiel diminue le solde dû sans clôturer l'obligation tant
que le montant restant est supérieur à zéro.

### RB-FIN-006 --- Paiement excédentaire

Un paiement supérieur au solde dû doit être traité selon une règle
explicite : crédit disponible, remboursement ou rejet. Il ne doit pas
être absorbé silencieusement.

### RB-FIN-007 --- Confirmation du paiement

Un paiement initié n'est pas considéré comme encaissé tant que sa
confirmation n'a pas été reçue et vérifiée selon le canal utilisé.

### RB-FIN-008 --- Idempotence

La réception répétée d'une même notification de paiement ne doit pas
créer plusieurs paiements ni plusieurs reçus. Une référence de
transaction unique doit permettre de détecter les doublons.

### RB-FIN-009 --- Vérification des paiements externes

Les callbacks Mobile Money ou bancaires doivent être authentifiés,
vérifiés, rapprochés d'une transaction attendue et contrôlés contre les
rejeux.

### RB-FIN-010 --- Reçu numéroté

Tout paiement confirmé doit produire un reçu identifiable, non ambigu et
rattaché au paiement. La numérotation doit respecter le périmètre défini
par la politique comptable.

### RB-FIN-011 --- Annulation et contre-écriture

Un paiement confirmé ne doit pas être supprimé. Son annulation doit
produire une opération compensatoire ou une contre-écriture traçable,
avec motif et autorisation.

### RB-FIN-012 --- Rapprochement

Les paiements reçus par banque ou Mobile Money doivent pouvoir être
rapprochés des transactions internes et des relevés externes.

### RB-FIN-013 --- Gestion multi-devises

Chaque opération conserve sa devise d'origine. Toute conversion doit
enregistrer le taux, la date, la source et la règle d'arrondi utilisés.

### RB-FIN-014 --- Caisse

Les opérations de caisse doivent être rattachées à une session, un
caissier, un fonds et un établissement. L'ouverture, les mouvements, la
clôture et les écarts doivent être historisés.

### RB-FIN-015 --- Séparation des tâches financières

Les rôles ADMIN, DIRECTION, ACCOUNTANT et CASHIER doivent disposer de
permissions distinctes. La validation d'une annulation ou d'un
remboursement peut exiger un second approbateur.

### RB-FIN-016 --- Créances et relances

Les relances doivent se baser sur un solde réel et une échéance
dépassée, tenir compte des paiements en cours de confirmation et
respecter les préférences de communication.

### RB-FIN-017 --- Remises et exonérations

Toute remise, bourse ou exonération doit avoir un motif, un auteur
habilité, une période de validité et, si nécessaire, un approbateur.

### RB-FIN-018 --- Comptabilité générale

Les opérations financières doivent pouvoir alimenter un journal
comptable équilibré selon un plan comptable configurable. Les écritures
validées ne sont pas modifiables directement ; elles sont corrigées par
écritures de régularisation.

### RB-FIN-019 --- Clôture financière

La clôture d'une période financière doit contrôler les paiements non
rapprochés, caisses non clôturées, opérations en attente et écritures
déséquilibrées.

## 10. Portails et communication

### RB-PORT-001 --- Portail parent

Le parent doit disposer d'un accès sécurisé aux informations autorisées
de ses enfants : résultats publiés, présences, communications, documents
et situation financière selon les permissions définies.

### RB-PORT-002 --- Portail élève

L'élève accède à ses résultats publiés, son emploi du temps, ses
absences et aux ressources pédagogiques autorisées.

### RB-PORT-003 --- Portail enseignant

L'enseignant accède à ses classes, affectations, listes, présences,
évaluations et communications pédagogiques.

### RB-PORT-004 --- Cohérence des données affichées

Les portails doivent lire les mêmes données métier de référence que les
modules internes. Ils ne doivent pas maintenir des copies indépendantes
modifiables des résultats ou paiements.

### RB-PORT-005 --- Confidentialité des notifications

Une notification ne doit pas révéler de note, dette ou donnée
personnelle à un numéro ou une adresse dont le rattachement n'est pas
vérifié.

### RB-PORT-006 --- Préférences de communication

Les préférences de canal et de langue peuvent être configurées, sous
réserve des notifications obligatoires et des règles de conservation des
preuves.

### RB-PORT-007 --- Historique de livraison

Le système doit conserver l'état d'envoi des notifications : préparée,
envoyée, délivrée, échouée ou en attente, lorsque le fournisseur permet
de connaître cet état.

## 11. Documents et archives

### RB-DOC-001 --- Document officiel vérifiable

Les bulletins, attestations, reçus et certificats officiels doivent
disposer d'un identifiant unique et de mécanismes de vérification
adaptés.

### RB-DOC-002 --- QR de vérification

Lorsqu'un QR code est utilisé, il doit permettre de vérifier
l'authenticité du document sans exposer des données personnelles non
nécessaires.

### RB-DOC-003 --- Version documentaire

Toute réédition ou correction d'un document officiel doit être
versionnée et traçable.

### RB-DOC-004 --- Accès documentaire

L'accès aux documents doit respecter le tenant, le rôle, le rattachement
à l'élève et le niveau de confidentialité.

### RB-DOC-005 --- Conservation

Les durées de conservation et les modalités d'archivage doivent être
configurables selon les obligations légales et contractuelles
applicables.

## 12. Ressources humaines et paie

### RB-HR-001 --- Dossier du personnel

Chaque membre du personnel possède un dossier distinct du compte d'accès
informatique. Le compte utilisateur ne constitue pas à lui seul un
dossier RH.

### RB-HR-002 --- Affectation du personnel

Les affectations à des classes, matières, fonctions ou établissements
doivent être datées et historisées.

### RB-HR-003 --- Confidentialité RH

Les données de paie, contrats et informations personnelles du personnel
ne sont accessibles qu'aux rôles RH et financiers autorisés.

### RB-HR-004 --- Calcul de paie traçable

Toute paie doit être calculée à partir d'éléments explicites, d'une
période, de règles versionnées et de validations.

### RB-HR-005 --- Séparation paie et paiement

La préparation ou validation d'une paie ne signifie pas que le paiement
a été exécuté. Le statut de paiement doit être suivi séparément.

## 13. Modules complémentaires : bibliothèque, transport, santé, internat et inventaire

### RB-OPS-001 --- Activation modulaire

Les modules complémentaires peuvent être activés par établissement selon
son contrat et ses besoins, sans rendre obligatoires les modules non
utilisés.

### RB-OPS-002 --- Bibliothèque

Tout prêt doit être lié à un exemplaire, un emprunteur, une date de
sortie et une date de retour prévue. Les retards et pertes doivent
suivre des règles configurées.

### RB-OPS-003 --- Transport scolaire

Une affectation au transport doit tenir compte de la ligne, de l'arrêt,
de la capacité, de la période et des autorisations de prise en charge.

### RB-OPS-004 --- Santé scolaire

Les données de santé doivent être isolées et soumises à des permissions
renforcées. Elles ne doivent pas être visibles dans les portails
ordinaires sans justification et autorisation appropriées.

### RB-OPS-005 --- Internat

L'affectation à un internat doit tenir compte des capacités, chambres,
périodes, responsables et règles de présence.

### RB-OPS-006 --- Inventaire

Tout mouvement de stock doit être enregistré avec article, quantité,
emplacement, date, auteur et motif. Les corrections d'inventaire doivent
être traçables.

## 14. Interopérabilité et intégrations

### RB-INT-001 --- API documentée

Toute fonctionnalité exposée à un système externe doit utiliser une API
documentée, versionnée et soumise à authentification et autorisation.

### RB-INT-002 --- Contrats stables

Les changements d'API susceptibles de casser les intégrations doivent
suivre une stratégie de versionnement et une période de dépréciation
documentée.

### RB-INT-003 --- OAuth2 et scopes

Les intégrations doivent utiliser des mécanismes d'authentification
adaptés, avec des scopes limitant les ressources et actions accessibles.

### RB-INT-004 --- Webhooks signés

Les webhooks sortants doivent être signés, horodatés, identifiables et
rejouables de manière contrôlée. Le destinataire doit pouvoir détecter
les doublons.

### RB-INT-005 --- Journal d'intégration

Chaque échange externe doit conserver son identifiant de corrélation,
son état, sa date, son système source ou destinataire et les erreurs
utiles au diagnostic, sans journaliser de secrets.

### RB-INT-006 --- Imports contrôlés

Les imports CSV/Excel doivent passer par une étape de prévisualisation,
validation, détection de doublons et rapport d'erreurs avant écriture
définitive.

### RB-INT-007 --- Exports autorisés

Tout export doit être limité au périmètre autorisé, journalisé et
protégé contre l'extraction excessive de données.

### RB-INT-008 --- OneRoster

EduNova doit prévoir une capacité d'échange des organisations,
utilisateurs, cours, inscriptions et résultats selon le standard
OneRoster, sous réserve de définir le profil d'implémentation et les
champs réellement pris en charge.

### RB-INT-009 --- LTI

EduNova peut exposer une intégration LTI 1.3 pour connecter des outils
pédagogiques externes, avec validation des rôles, contextes, lancements
et retours de résultats.

### RB-INT-010 --- Ed-Fi

L'architecture de données doit pouvoir être mappée vers le modèle Ed-Fi
lorsque cela est pertinent pour les échanges avec des systèmes éducatifs
institutionnels. Ce mapping ne doit pas imposer une duplication inutile
du modèle interne.

### RB-INT-011 --- SSO

Les intégrations d'identité peuvent utiliser un mécanisme SSO standard,
avec rattachement explicite des identités externes aux comptes EduNova.

### RB-INT-012 --- Connecteurs découplés

Chaque intégration externe doit être isolée derrière un adaptateur ou
connecteur. La logique métier centrale ne doit pas dépendre directement
du SDK d'un fournisseur.

### RB-INT-013 --- Résilience des intégrations

Une panne d'un fournisseur externe ne doit pas corrompre les données
internes. Les opérations peuvent être mises en attente, retentées avec
stratégie contrôlée ou soumises à intervention.

### RB-INT-014 --- Exportabilité

Un établissement doit pouvoir récupérer ses données dans des formats
documentés, dans le respect des droits, de la sécurité, des contrats et
des obligations légales.

## 15. Architecture événementielle et workflows

### RB-WF-001 --- États métier explicites

Les processus sensibles doivent être modélisés par des états et
transitions autorisées, plutôt que par des indicateurs booléens
dispersés.

### RB-WF-002 --- Transitions gardées

Chaque transition doit vérifier les préconditions, les permissions, les
invariants et les éventuelles validations requises.

### RB-WF-003 --- Historique du workflow

Chaque changement d'état doit enregistrer l'acteur, la date, le motif et
la transition exécutée.

### RB-WF-004 --- Événements métier

Les événements doivent exprimer des faits métier accomplis, par exemple
`StudentAdmitted`, `EnrollmentValidated`, `PaymentConfirmed`,
`ResultsApproved` ou `ReportCardPublished`.

### RB-WF-005 --- Événement après transaction

Un événement annonçant une opération validée ne doit être publié
qu'après la persistance cohérente de cette opération. Une stratégie de
type transactional outbox doit être envisagée pour éviter les pertes ou
doubles publications.

### RB-WF-006 --- Consommateurs idempotents

Tout consommateur d'événement doit pouvoir traiter plusieurs fois le
même événement sans produire plusieurs effets métier.

### RB-WF-007 --- Reprise et compensation

Les workflows interrompus doivent pouvoir être repris ou compensés sans
réexécuter aveuglément les étapes déjà confirmées.

### RB-WF-008 --- Validation humaine

Les décisions ayant un impact officiel, académique ou financier doivent
rester soumises à une validation humaine lorsque la politique métier
l'exige.

### RB-WF-009 --- Délais et escalades

Les workflows peuvent définir des délais, rappels et escalades, mais ces
automatismes ne doivent pas approuver une opération sensible par défaut.

## 16. Mode hors ligne et synchronisation

### RB-OFF-001 --- Périmètre hors ligne explicite

Seules les fonctions identifiées comme compatibles hors ligne peuvent
être utilisées sans connexion. Les opérations critiques nécessitant une
validation serveur doivent rester en attente.

### RB-OFF-002 --- Identifiant d'opération

Chaque opération hors ligne doit recevoir un identifiant unique généré
côté client afin de prévenir les doublons lors de la synchronisation.

### RB-OFF-003 --- Horodatages distincts

Le système doit distinguer l'heure de saisie locale, l'heure de
réception serveur et l'heure de validation métier.

### RB-OFF-004 --- Conflits non silencieux

Un conflit de synchronisation ne doit pas écraser silencieusement une
donnée validée. Il doit suivre une règle de résolution explicite ou être
soumis à arbitrage.

### RB-OFF-005 --- Contrôle serveur

Les autorisations, contraintes et validations métier doivent être
réévaluées côté serveur lors de la synchronisation.

## 17. Sécurité, audit et protection des données

### RB-SEC-001 --- Validation côté serveur

Aucune validation effectuée uniquement dans l'interface cliente ne doit
être considérée comme une garantie de sécurité.

### RB-SEC-002 --- Protection contre les accès inter-tenant

Les requêtes doivent appliquer les contraintes tenant au niveau des
services et dépôts de données. Les tests doivent vérifier les tentatives
d'accès à une ressource d'un autre tenant.

### RB-SEC-003 --- Secrets

Les mots de passe, clés API, secrets MFA et jetons ne doivent jamais
être stockés en clair ni apparaître dans les journaux ou réponses API.

### RB-SEC-004 --- Limitation des tentatives

Les opérations d'authentification, de récupération de compte, de
validation MFA et les endpoints sensibles doivent être protégés contre
les tentatives automatisées.

### RB-SEC-005 --- Journal d'audit non altérable par les rôles ordinaires

Les utilisateurs métier ne doivent pas pouvoir modifier ou supprimer les
traces d'audit qui les concernent.

### RB-SEC-006 --- Minimisation

Chaque écran, API, export et notification ne doit exposer que les
données nécessaires à l'action autorisée.

### RB-SEC-007 --- Sauvegardes et restauration

Les sauvegardes doivent être planifiées, protégées et testées par des
exercices de restauration. Une sauvegarde non testée ne constitue pas
une garantie suffisante.

### RB-SEC-008 --- Gestion des incidents

Les incidents de sécurité doivent être enregistrés, qualifiés, traités
et clôturés selon une procédure documentée.

### RB-SEC-009 --- Tests de sécurité

Les tests doivent couvrir l'authentification, l'autorisation,
l'isolation tenant, les injections, les abus d'API, les imports, les
webhooks et les opérations financières.

### RB-SEC-010 --- Conformité locale

Les traitements de données doivent être évalués au regard du cadre légal
applicable en RDC et des juridictions dans lesquelles EduNova sera
exploité. Toute affirmation de conformité doit être validée
juridiquement.

## 18. Analytique, tableaux de bord et indicateurs

### RB-ANA-001 --- Indicateurs définis

Chaque indicateur doit avoir une définition métier, une formule, un
périmètre, une fréquence de mise à jour et un propriétaire.

### RB-ANA-002 --- Données validées

Les indicateurs officiels ne doivent pas mélanger données provisoires et
données validées sans distinction visible.

### RB-ANA-003 --- Filtrage tenant

Les tableaux de bord doivent respecter les mêmes règles d'isolation et
d'autorisation que les modules opérationnels.

### RB-ANA-004 --- Traçabilité des chiffres

Un indicateur doit pouvoir être expliqué à partir des données et règles
ayant servi à son calcul.

### RB-ANA-005 --- Pas de classement trompeur

Les comparaisons entre classes, établissements ou périodes doivent tenir
compte des différences de périmètre et de configuration.

## 19. Intelligence artificielle et assistance décisionnelle

### RB-AI-001 --- IA assistive par défaut

L'IA peut assister la rédaction, la recherche, la synthèse, la détection
d'anomalies et l'aide à la décision. Elle ne remplace pas
automatiquement l'autorité scolaire ou financière.

### RB-AI-002 --- Pas de décision officielle autonome

L'IA ne peut valider seule une admission, une note, une délibération,
une promotion, une sanction, une remise ou un paiement.

### RB-AI-003 --- Données minimisées

Seules les données nécessaires à la tâche peuvent être transmises à un
fournisseur IA. Les données personnelles doivent être masquées ou
pseudonymisées lorsque possible.

### RB-AI-004 --- Fournisseurs interchangeables

Les fournisseurs IA doivent être accessibles par une couche
d'abstraction afin d'éviter une dépendance irréversible à un
fournisseur.

### RB-AI-005 --- Sortie IA non fiable par défaut

Toute sortie IA doit être considérée comme une proposition à vérifier.
Les actions exécutables doivent être contrôlées par des règles
déterministes et des permissions serveur.

### RB-AI-006 --- Traçabilité

Les usages IA ayant un impact métier doivent conserver le fournisseur,
le modèle, la version de prompt ou de politique, le contexte non
sensible utile et le résultat de validation humaine.

### RB-AI-007 --- Explicabilité des recommandations

Une recommandation IA doit présenter ses limites, les données prises en
compte et les raisons principales de la suggestion, dans la mesure
permise par la technique.

### RB-AI-008 --- Protection contre l'exfiltration

Les agents et outils IA ne doivent pas pouvoir accéder à des données ou
exécuter des actions au-delà des permissions de l'utilisateur et du
tenant.

### RB-AI-009 --- Évaluation continue

Les fonctionnalités IA doivent être évaluées sur la qualité, les biais,
la sécurité, les coûts, la latence et les taux d'erreur avant et après
déploiement.

## 20. Cycle de vie de bout en bout --- invariants transversaux

### RB-E2E-001 --- Admission vers inscription

Une admission acceptée peut déclencher une tâche d'inscription, mais
l'inscription n'est validée qu'après vérification des conditions
administratives requises.

### RB-E2E-002 --- Inscription vers affectation

Une inscription validée doit être suivie d'une affectation scolaire
valide avant l'accès aux opérations pédagogiques régulières.

### RB-E2E-003 --- Affectation vers pédagogie

Les listes de classe, cours, présences et évaluations doivent se baser
sur les affectations actives à la date concernée.

### RB-E2E-004 --- Évaluation vers bulletin

Les notes ne deviennent visibles comme résultats officiels qu'après
validation et publication selon le workflow.

### RB-E2E-005 --- Résultat vers promotion

La promotion doit utiliser la décision officielle de délibération et la
configuration de l'année suivante.
