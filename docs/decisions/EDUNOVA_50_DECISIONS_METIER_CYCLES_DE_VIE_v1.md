# EDUNOVA --- 50 décisions métier et cycles de vie de bout en bout

**Version :** 1.0 --- **Date :** 21 novembre 2026\
**Périmètre :** ERP scolaire SaaS multi-établissements, RDC puis
international.\
**Statut :** DM-001 et DM-002 ratifiées ; DM-003 à DM-050 sont des
décisions directrices recommandées, à ratifier progressivement.

## 0. Portée et gouvernance

Ce document couvre les fonctionnalités existantes, les fonctionnalités
incomplètes et les extensions futures. Il complète le document
`EDUNOVA_REGLES_METIER_CONSOLIDEES_v1.md` ; il ne le remplace pas.

**Important :** « prendre les décisions » signifie ici proposer une
ligne de conduite cohérente et complète. Les décisions DM-001 et DM-002
ont été expressément ratifiées par le propriétaire. Les autres sont des
recommandations structurantes et ne doivent pas être étiquetées
ratifiées sans confirmation explicite. Les règles juridiques, fiscales,
comptables et de conservation doivent être validées dans chaque
juridiction.

Principes communs : 1. Chaque donnée métier a un module propriétaire et
une source de vérité. 2. Chaque objet possède des états explicites et
des transitions autorisées. 3. Toute transition précise préconditions,
acteur, permissions, effets et erreurs. 4. Une donnée officielle n'est
pas effacée pour corriger une erreur : correction versionnée ou
opération compensatoire. 5. L'isolation tenant s'applique aux lectures,
écritures, recherches, exports, tâches différées, fichiers et
intégrations. 6. Les opérations sensibles sont traçables ; les journaux
ne contiennent jamais de secrets. 7. Les automatisations sont
idempotentes, explicables, supervisables et récupérables. 8. Les
décisions académiques, financières et disciplinaires restent humaines
lorsque leur impact l'exige. 9. Les configurations ayant influencé une
opération historique restent identifiables. 10. Une fonctionnalité n'est
terminée qu'après validation de son parcours nominal et de ses
exceptions.

Pour chaque cycle, les états sont des repères métier, pas une obligation
d'utiliser les mêmes noms dans tous les modules. « Annulé » ne signifie
pas « supprimé » ; « publié » signifie visible dans le périmètre
autorisé ; « archivé » signifie conservé selon une politique d'accès et
de rétention.

------------------------------------------------------------------------

# 1. Gouvernance et fondations transversales

## DM-001 --- Gouvernance universelle et progressive des cycles de vie

**Statut : RATIFIÉE --- choix 2.**

**Décision :** toutes les fonctionnalités existantes et futures doivent
avoir un cycle de vie métier documenté, adapté au domaine, puis être
remises à niveau progressivement selon leur criticité.

**Règles :** documenter objets, états, transitions, acteurs,
préconditions, effets, exceptions, annulation, correction, clôture,
archivage et réouverture éventuelle. Toute fonctionnalité doit avoir des
tests de bout en bout et une validation métier.

**Cycle de vie d'une fonctionnalité :** idée → cadrage → règles métier →
analyse d'impacts → approbation → spécification → réalisation → tests →
validation métier → mise en service → surveillance → évolution →
dépréciation → retrait contrôlé.

**Acceptation :** aucune fonctionnalité n'est considérée terminée sur la
seule base de son interface.

## DM-002 --- Référentiel commun des états métier, adapté par domaine

**Statut : RATIFIÉE --- choix 2.**

**Décision :** EduNova définit des principes communs de gestion des
états, mais chaque domaine conserve ses états et transitions
spécifiques.

**Règles :** chaque état a une signification non ambiguë ; chaque
transition définit préconditions, permissions, acteur, effets et motif ;
un module ne modifie pas directement l'état d'un objet dont un autre
module est propriétaire ; les états historiques restent consultables
selon les droits.

**Cycle :** besoin → définition de l'état → transitions → permissions →
effets → exceptions → tests → approbation → surveillance.

**Acceptation :** toute transition non définie ou non autorisée est
rejetée ; les interfaces distinguent les données provisoires des données
officielles.

## DM-003 --- Audit des opérations métier

**Statut : recommandation à ratifier.**

**Décision :** journaliser toute opération métier significative, avec
protection renforcée des traces sensibles.

**Règles :** tracer acteur, tenant, objet, action, date serveur,
résultat, motif et identifiant de corrélation ; conserver les
différences avant/après lorsque pertinent ; exclure secrets, mots de
passe et jetons ; limiter consultation et export ; appliquer une
politique de rétention.

**Cycle :** opération → qualification → journalisation → protection →
consultation autorisée → export éventuel → rétention → archivage/purge
autorisée.

**Acceptation :** une opération sensible est reconstituable ; les
utilisateurs ordinaires ne peuvent altérer les traces.

## DM-004 --- Isolation stricte multi-tenant

**Statut : recommandation à ratifier.**

**Décision :** toute ressource scolaire appartient à un tenant explicite
; un identifiant ne vaut jamais autorisation.

**Règles :** vérifier tenant et permissions côté serveur pour chaque
lecture/écriture ; appliquer le filtre aux recherches, fichiers,
exports, rapports, événements et tâches asynchrones ; encadrer les accès
de support inter-tenant ; suspendre sans détruire les archives.

**Cycle :** prospect → provisionné → configuré → actif →
suspendu/réactivé → résilié → restitution/export contrôlé → archivage →
purge autorisée.

**Acceptation :** tests d'accès croisé négatifs sur chaque type de
ressource.

## DM-005 --- Séparation identité, compte et rattachement

**Statut : recommandation à ratifier.**

**Décision :** distinguer l'identité d'une personne, son compte
d'authentification et ses rattachements aux établissements.

**Règles :** une personne peut avoir plusieurs rattachements ; aucun
rôle n'est implicite ; la désactivation du compte ne supprime pas le
dossier métier ; les doublons incertains sont soumis à revue humaine.

**Cycle :** identité déclarée → vérification → compte créé/lié →
rattachement demandé → approbation → accès actif → changement →
suspension/révocation → réactivation/clôture.

**Acceptation :** aucun accès sans rattachement actif et permission
explicite.

## DM-006 --- Rôles, permissions et séparation des tâches

**Statut : recommandation à ratifier.**

**Décision :** autoriser par action, ressource, tenant et périmètre ;
séparer administration, scolarité, pédagogie, finance, RH et portails.

**Règles :** moindre privilège ; délégations limitées dans le temps ;
double approbation lorsque le risque l'exige ; revue périodique des
droits ; une permission finance ne remplace jamais une permission
scolaire.

**Cycle :** demande → justification → approbation → attribution →
utilisation → revue → modification/expiration → révocation → audit.

**Acceptation :** matrice rôle-action testée, y compris les refus.

## DM-007 --- Configuration versionnée et non rétroactive

**Statut : recommandation à ratifier.**

**Décision :** toute configuration influençant un résultat, montant,
document ou affectation est versionnée et datée.

**Règles :** séparer configuration scolaire et académique ; conserver la
version utilisée ; toute modification rétroactive exige autorisation,
motif et analyse d'impact.

**Cycle :** brouillon → vérification → approbation → planification →
activation → utilisation → remplacement → archivage.

**Acceptation :** un résultat historique est reproductible avec les
règles applicables à l'époque.

## DM-008 --- Suppression, annulation et correction

**Statut : recommandation à ratifier.**

**Décision :** interdire la suppression destructive des données
officielles, financières et historiques.

**Règles :** distinguer suppression d'un brouillon, annulation métier,
correction, compensation et purge légalement autorisée ; conserver
l'objet d'origine et son motif ; préserver les liens entre dossiers,
résultats, paiements et documents.

**Cycle :** demande → qualification → analyse des dépendances →
approbation → correction/compensation → notification → audit →
rétention.

**Acceptation :** aucune correction ne réécrit silencieusement
l'histoire.

## DM-009 --- Notifications sur événements confirmés

**Statut : recommandation à ratifier.**

**Décision :** ne notifier que sur un événement métier confirmé, jamais
sur une simple tentative.

**Règles :** vérifier destinataire, rattachement et confidentialité ;
distinguer statut métier et statut de livraison ; dédupliquer ; retenter
selon une politique bornée ; une notification ne valide jamais
l'opération source.

**Cycle :** événement confirmé → règle → résolution destinataire →
contrôle → mise en file → envoi → délivrée/échouée → reprise ou clôture.

**Acceptation :** aucune notification de paiement encaissé avant
confirmation réelle.

## DM-010 --- Incidents, sauvegarde et continuité

**Statut : recommandation à ratifier.**

**Décision :** traiter tout incident affectant confidentialité,
intégrité ou disponibilité par un processus contrôlé.

**Règles :** qualifier gravité et périmètre ; préserver les preuves ;
confiner ; restaurer depuis des sauvegardes protégées ; tester
régulièrement la restauration ; séparer correction d'urgence et
correction définitive.

**Cycle :** détection → qualification → confinement → investigation →
restauration/correction → vérification → communication → clôture →
retour d'expérience.

**Acceptation :** restauration testée et chronologie d'incident
documentée.

------------------------------------------------------------------------

# 2. Élèves, admissions et inscriptions

## DM-011 --- Préinscription et admission

**Statut : recommandation à ratifier.**

**Décision :** une préinscription est une demande, distincte de
l'admission et de l'inscription définitive.

**Règles :** pièces manquantes visibles ; contrôle de doublons sans
fusion automatique ; admission décidée par un acteur habilité ;
acceptation conditionnelle assortie de conditions et délais ; rejet
motivé.

**Cycle :** demande → soumise → dossier incomplet/en vérification →
décision (acceptée, conditionnelle, attente, refusée) → conditions
levées → inscription ou clôture.

**Acceptation :** une demande acceptée ne crée pas silencieusement une
inscription complète.

## DM-012 --- Dossier maître de l'élève

**Statut : recommandation à ratifier.**

**Décision :** conserver un dossier maître d'identité distinct des
inscriptions annuelles.

**Règles :** identité et pièces vérifiées ; changements sensibles
justifiés ; doublons incertains revus manuellement ; une nouvelle année
crée un nouveau rattachement, pas une nouvelle personne.

**Cycle :** créé → vérifié → actif → mis à jour avec historique →
suspendu/clos → archivé → réactivé.

**Acceptation :** un élève réinscrit conserve son historique sans
doublon.

## DM-013 --- Inscription annuelle

**Statut : recommandation à ratifier.**

**Décision :** l'inscription est un acte administratif annuel, distinct
de l'admission et de l'affectation.

**Règles :** vérifier admission, pièces et conditions ; aucun frais
n'est créé par défaut à la seule création d'une inscription ; les
conditions restantes sont explicites.

**Cycle :** préparée → pièces contrôlées → soumise → validée/rejetée →
affectation attendue → active → suspendue/annulée → clôturée → archivée.

**Acceptation :** aucune activité pédagogique régulière sans inscription
valide ou dérogation tracée.

## DM-014 --- Affectation et changement de classe

**Statut : recommandation à ratifier.**

**Décision :** une affectation relie l'élève à l'année, au niveau, à la
classe et éventuellement à l'option/groupe, avec dates d'effet.

**Règles :** vérifier capacité et compatibilité ; historiser chaque
mutation ; analyser les impacts sur notes, présences et frais ; ne
jamais réécrire l'affectation précédente.

**Cycle :** demande → contrôle → approbation → active → demande de
changement → nouvelle affectation datée → clôture ancienne affectation →
historique.

**Acceptation :** aucune double affectation incompatible ; listes
calculées selon la date de référence.

## DM-015 --- Transfert entrant et sortant

**Statut : recommandation à ratifier.**

**Décision :** le transfert déplace le rattachement scolaire, pas la
propriété ni l'historique des données d'un tenant.

**Règles :** distinguer demande, autorisation, documents et confirmation
d'arrivée ; identifier l'origine des données ; vérifier les équivalences
; ne pas transférer automatiquement une dette comme obligation du nouvel
établissement.

**Cycle :** demande → vérification → autorisation sortante → dossier de
transfert → clôture du rattachement → demande entrante → validation →
inscription/affectation locale.

**Acceptation :** continuité documentaire sans accès inter-tenant
implicite.

## DM-016 --- Promotion, redoublement et réorientation

**Statut : recommandation à ratifier.**

**Décision :** la promotion dépend d'une décision officielle validée et
des règles de passage applicables.

**Règles :** aucun résultat provisoire ne déclenche une promotion ;
décisions admis, ajourné, redoublement et réorientation distinctes ;
dérogations motivées ; nouvelle affectation pour l'année suivante.

**Cycle :** résultats consolidés → délibération validée → décision
officielle → contrôle → proposition d'affectation → approbation →
nouvelle affectation → clôture année précédente.

**Acceptation :** statut ADMITTED exigé lorsque la règle de promotion le
prévoit.

## DM-017 --- Sortie et réactivation

**Statut : recommandation à ratifier.**

**Décision :** la sortie clôt le rattachement actif, pas l'identité ni
les archives de l'élève.

**Règles :** motif et date d'effet ; accès opérationnels révoqués ;
résultats, paiements et documents conservés selon politique ; un retour
crée une nouvelle inscription sur le dossier maître existant.

**Cycle :** demande → contrôle → décision → clôture rattachement →
documents → archivage → demande de retour → vérification → nouvelle
inscription.

**Acceptation :** aucune suppression des historiques lors d'une sortie.

## DM-018 --- Responsables légaux et liens parent-enfant

**Statut : recommandation à ratifier.**

**Décision :** les liens parent/tuteur sont explicites, vérifiés, datés
et assortis d'un périmètre d'accès.

**Règles :** gérer plusieurs responsables et plusieurs enfants ; prendre
en compte restrictions ; retirer les accès lorsque le lien expire ou est
révoqué ; ne pas confondre lien déclaré et accès vérifié.

**Cycle :** demande → preuve → vérification → approbation → accès →
modification/restriction → révocation → audit.

**Acceptation :** aucun accès parent par simple connaissance d'un
identifiant élève.

------------------------------------------------------------------------

# 3. Configuration scolaire et académique

## DM-019 --- Année scolaire

**Statut : recommandation à ratifier.**

**Décision :** l'année scolaire est le cadre temporel commun des
inscriptions, affectations, calendriers, évaluations et finances.

**Règles :** dates, périodes et périmètre explicites ; ouverture
conditionnée à la configuration minimale ; clôture avec contrôle des
opérations pendantes ; réouverture exceptionnelle autorisée.

**Cycle :** préparée → configurée → approuvée → ouverte → en cours →
pré-clôture → clôturée → archivée (réouverture exceptionnelle →
reclôture).

**Acceptation :** aucune opération ordinaire dans une année non ouverte
ou clôturée.

## DM-020 --- Structure scolaire

**Statut : recommandation à ratifier.**

**Décision :** niveaux, classes, options et groupes sont un référentiel
versionné, distinct des cours et des règles de notation.

**Règles :** capacité et compatibilité contrôlées ; codes uniques dans
leur portée ; structure inactive non affectable ; historique non
supprimé.

**Cycle :** brouillon → contrôle → approbation → activation →
affectations → modification versionnée → désactivation → archivage.

**Acceptation :** une classe référencée par l'historique ne peut être
supprimée.

## DM-021 --- Calendrier scolaire et périodes

**Statut : recommandation à ratifier.**

**Décision :** le calendrier définit enseignement, congés, examens,
clôtures et échéances.

**Règles :** dates cohérentes ; chevauchements détectés ; modification
en cours d'année approuvée et communiquée ; date applicable conservée
sur les opérations.

**Cycle :** projet → validation → publication → actif → modification
exceptionnelle → clôture → archivage.

**Acceptation :** toute activité hors fenêtre possède une dérogation
tracée.

## DM-022 --- Matières, programmes et coefficients

**Statut : recommandation à ratifier.**

**Décision :** matières et programmes sont définis par
niveau/classe/option ; coefficients, barèmes et seuils sont versionnés.

**Règles :** matière prévue avant évaluation ; contrôles des
coefficients ; modification après début de période soumise à approbation
et analyse d'impact ; calcul historique lié à la version.

**Cycle :** conception → revue pédagogique → approbation → activation →
utilisation → remplacement versionné → archivage.

**Acceptation :** calcul historique reproductible.

## DM-023 --- Affectation des enseignants

**Statut : recommandation à ratifier.**

**Décision :** les droits pédagogiques découlent d'une affectation datée
à des classes, matières et périodes.

**Règles :** distinguer compte utilisateur et dossier RH ; contrôler
charge et compatibilité ; gérer remplacements ; retirer les droits
opérationnels à la fin de l'affectation.

**Cycle :** proposition → vérification → approbation → affectation
active → remplacement/modification → fin → archivage.

**Acceptation :** un enseignant non affecté ne peut saisir ni consulter
les données pédagogiques de la classe.

## DM-024 --- Emploi du temps et séances

**Statut : recommandation à ratifier.**

**Décision :** une séance relie classe/groupe, matière, enseignant,
salle, date et créneau.

**Règles :** détecter conflits ; distinguer planifiée, tenue, reportée
et annulée ; historiser les modifications ; communiquer les changements.

**Cycle :** brouillon → contrôle conflits → publication → planifiée →
tenue/reportée/annulée → clôturée → historique.

**Acceptation :** aucun conflit non résolu lors de la publication.

------------------------------------------------------------------------

# 4. Présences, évaluations et résultats

## DM-025 --- Présences, absences et retards

**Statut : recommandation à ratifier.**

**Décision :** chaque présence est liée à un élève, une séance/période,
une classe et une date ; absence, retard, présence et non-saisie sont
distincts.

**Règles :** saisie par acteur habilité ; correction motivée et
historisée ; justification séparée ; aucune absence convertie
automatiquement en zéro ou sanction.

**Cycle :** séance planifiée → feuille ouverte → saisie → soumission →
vérification/validation → justification éventuelle → correction
contrôlée → clôture.

**Acceptation :** auteur et date de correction identifiables.

## DM-026 --- Évaluation et devoir

**Statut : recommandation à ratifier.**

**Décision :** une évaluation est définie avant la tenue avec matière,
classe, période, barème, coefficient, date et auteur.

**Règles :** paramètres figés pour les notes ; report/annulation motivé
; absence enregistrée distinctement ; évaluation de remplacement
identifiable.

**Cycle :** brouillon → contrôle configuration → approbation/publication
→ planifiée → tenue → collecte résultats → clôture → archivage.

**Acceptation :** aucune note orpheline ou sans barème applicable.

## DM-027 --- Saisie et validation des notes

**Statut : recommandation à ratifier.**

**Décision :** la saisie ne constitue pas une validation officielle.

**Règles :** contrôler bornes, barème, élève, matière et évaluation ;
distinguer brouillon, soumis, vérifié, validé et publié ; après
verrouillage, correction par procédure motivée.

**Cycle :** saisie → contrôle enseignant → soumission → vérification →
correction ou validation → verrouillage → publication.

**Acceptation :** toute modification non autorisée est rejetée ; auteur
et approbateur sont traçables.

## DM-028 --- Calcul des moyennes et résultats

**Statut : recommandation à ratifier.**

**Décision :** tout calcul officiel est déterministe, reproductible et
lié aux données et versions de règles utilisées.

**Règles :** définir absences, notes manquantes, coefficients et
arrondis ; résultat incomplet marqué provisoire ; changement de règle
non rétroactif silencieux ; recalcul officiel versionné.

**Cycle :** collecte → contrôle complétude → calcul provisoire →
vérification → calcul officiel → validation → gel/version → recalcul
exceptionnel.

**Acceptation :** résultats reproductibles et cas limites testés.

## DM-029 --- Clôture des périodes académiques

**Statut : recommandation à ratifier.**

**Décision :** une période n'est clôturée qu'après contrôle des notes,
présences, évaluations et exceptions.

**Règles :** anomalies bloquantes/non bloquantes ; responsable désigné ;
dérogation documentée ; modification après clôture par réouverture
autorisée ou rectification versionnée.

**Cycle :** ouverte → pré-clôture → contrôles → corrections → prête →
approuvée → clôturée → réouverture exceptionnelle → reclôture.

**Acceptation :** aucune clôture silencieuse avec données obligatoires
manquantes.

## DM-030 --- Délibération

**Statut : recommandation à ratifier.**

**Décision :** la délibération est une décision officielle d'une
instance habilitée, fondée sur des résultats consolidés.

**Règles :** participants, résultats, règles, anomalies et motifs
conservés ; décisions explicites ; dérogations motivées ; l'IA prépare
et explique mais ne vote ni ne valide.

**Cycle :** dossier préparé → contrôlé → session → délibération →
décisions saisies → validation → procès-verbal → publication →
contestation/rectification → archivage.

**Acceptation :** aucune promotion depuis une délibération non validée.

## DM-031 --- Bulletin et relevé de notes

**Statut : recommandation à ratifier.**

**Décision :** tout bulletin publié est un document officiel immuable et
versionné.

**Règles :** généré depuis résultats validés ; brouillon clairement
marqué ; publication contrôlée ; correction par nouvelle version liée à
l'ancienne ; accès limité aux destinataires autorisés.

**Cycle :** données validées → génération → contrôle → approbation →
publication → consultation → rectification versionnée → archivage.

**Acceptation :** version officielle reproductible et vérifiable.

## DM-032 --- Contestation et rectification académique

**Statut : recommandation à ratifier.**

**Décision :** toute contestation de note, bulletin ou décision est un
dossier instruit sans écraser l'état officiel initial.

**Règles :** demandeur, délai, objet, motif et pièces ; instruction par
rôle autorisé ; décision motivée ; impacts recalculés sur moyenne,
bulletin, délibération et promotion.

**Cycle :** demande → recevabilité → instruction → décision → correction
versionnée ou rejet → notification → clôture.

**Acceptation :** chaîne d'impacts complète et historique conservé.

------------------------------------------------------------------------

# 5. Finance, caisse et comptabilité

## DM-033 --- Barèmes et frais scolaires

**Statut : recommandation à ratifier.**

**Décision :** les frais proviennent d'un barème approuvé, versionné et
associé à un établissement, une année, un niveau/catégorie et une
devise.

**Règles :** postes, montants et échéances explicites ; remise distincte
; aucune génération implicite à la création d'un élève ou d'une
inscription ; pas de modification rétroactive silencieuse.

**Cycle :** préparation → contrôle → approbation → publication →
application → remplacement versionné → clôture → archivage.

**Acceptation :** chaque obligation référence la version du barème.

## DM-034 --- Obligations financières et échéanciers

**Statut : recommandation à ratifier.**

**Décision :** l'obligation est distincte du paiement et précise
origine, bénéficiaire, montant, devise, échéance et statut.

**Règles :** distinguer brut, remise, net, payé, crédit et solde ;
paiement partiel diminue le solde ; échéances liées à l'obligation ;
exonération autorisée.

**Cycle :** règle approuvée → obligation générée → vérifiée → publiée →
échéances → imputations → soldée/contestée/annulée → clôturée.

**Acceptation :** solde reproductible et aucune double facturation.

## DM-035 --- Initiation et confirmation de paiement

**Statut : recommandation à ratifier.**

**Décision :** un paiement initié n'est pas encaissé avant confirmation
vérifiée du canal ou du caissier autorisé.

**Règles :** états initié, en attente, confirmé, rejeté, expiré, suspect
et remboursé ; vérifier montant/devise/référence ; callbacks
authentifiés et anti-rejeu ; idempotence obligatoire.

**Cycle :** demande → référence → instruction → attente →
confirmation/rejet → imputation → reçu → rapprochement → clôture.

**Acceptation :** callback répété sans double paiement ni reçu.

## DM-036 --- Paiements partiels, excédents et crédits

**Statut : recommandation à ratifier.**

**Décision :** traiter explicitement paiement partiel et excédent.

**Règles :** un partiel laisse un solde ; excédent rejeté, crédité ou
remboursé selon politique ; réaffectation à une autre obligation
autorisée et tracée ; aucune absorption silencieuse.

**Cycle :** paiement confirmé → calcul solde → imputation → reste
dû/crédit → affectation ou remboursement approuvé → rapprochement →
clôture.

**Acceptation :** montant imputé + crédit/remboursement = paiement
confirmé.

## DM-037 --- Reçus, annulations et remboursements

**Statut : recommandation à ratifier.**

**Décision :** tout paiement confirmé génère un reçu unique ; annulation
et remboursement sont des opérations compensatoires.

**Règles :** numéro non réutilisé ; copie identique pour réédition ;
correction versionnée ; annulation visible comme telle ; remboursement
avec demande, approbation, exécution et preuve.

**Cycle :** paiement confirmé → reçu → délivrance → demande
d'annulation/remboursement → contrôle → approbation → contre-opération →
clôture.

**Acceptation :** aucun reçu confirmé supprimé.

## DM-038 --- Caisse et sessions de caissier

**Statut : recommandation à ratifier.**

**Décision :** toute opération espèces est liée à une session de caisse,
un caissier et un fonds.

**Règles :** solde initial ; mouvements motivés ; comptage réel ;
rapprochement théorique/réel ; écarts documentés et approuvés ; pas
d'opération sur caisse close.

**Cycle :** ouverture → fonds initial → mouvements → comptage →
rapprochement → clôture provisoire → validation → session close → audit.

**Acceptation :** total de session réconciliable.

## DM-039 --- Remises, bourses et exonérations

**Statut : recommandation à ratifier.**

**Décision :** une réduction est une décision autonome, justifiée,
bornée dans le temps et soumise à approbation selon seuil.

**Règles :** bénéficiaire, motif, montant/taux, postes, période et
approbateur ; contrôle de cumul ; ajustement explicite des obligations ;
expiration.

**Cycle :** demande → pièces → évaluation → approbation/rejet →
application → revue/renouvellement → expiration/révocation → audit.

**Acceptation :** effet financier recalculable et autorité identifiable.

## DM-040 --- Comptabilité, rapprochement et clôture financière

**Statut : recommandation à ratifier.**

**Décision :** les opérations financières alimentent une comptabilité
traçable ; les écritures validées sont corrigées par régularisation, pas
modifiées directement.

**Règles :** plan comptable validé par professionnel ; écritures
équilibrées et liées à leur source ; rapprochement des relevés ;
contrôle des opérations en attente avant clôture.

**Cycle :** opération confirmée → écriture provisoire → contrôle →
validation → rapprochement → pré-clôture → résolution écarts → clôture →
archivage.

**Acceptation :** piste d'audit paiement-reçu-écriture et équilibre
débit/crédit.

------------------------------------------------------------------------

# 6. Portails, documents et communication

## DM-041 --- Portail parent

**Statut : recommandation à ratifier.**

**Décision :** un parent consulte uniquement les enfants auxquels un
lien vérifié lui donne accès.

**Règles :** résultats après publication ; finance selon permission ;
demandes de justification/contestation suivies comme dossiers ;
révocation lors de changement de rattachement.

**Cycle :** invitation → vérification identité/lien → activation →
consultation → demande → traitement → notification → révocation/clôture.

**Acceptation :** tests parent autorisé, non autorisé, plusieurs enfants
et lien révoqué.

## DM-042 --- Portail élève

**Statut : recommandation à ratifier.**

**Décision :** l'élève accède à ses résultats publiés, emploi du temps,
présences et ressources autorisées.

**Règles :** données de référence communes ; aucune donnée d'un autre
élève ; accès adapté au statut et à la politique ; suspension liée à la
sortie selon règles de conservation.

**Cycle :** compte lié → activation → consultation → changement
d'affectation/année → suspension/clôture → archivage.

**Acceptation :** isolation par élève et respect des statuts de
publication.

## DM-043 --- Portail enseignant

**Statut : recommandation à ratifier.**

**Décision :** l'enseignant accède uniquement aux classes, matières et
périodes de ses affectations.

**Règles :** saisie selon état de période/évaluation ; soumission
verrouille les modifications ordinaires ; correction par procédure ; fin
d'affectation retire les droits opérationnels mais conserve
l'historique.

**Cycle :** rattachement → affectation → accès → saisie/soumission →
correction autorisée → fin d'affectation → révocation des droits →
historique.

**Acceptation :** accès hors affectation refusé.

## DM-044 --- Documents officiels, QR et vérification

**Statut : recommandation à ratifier.**

**Décision :** bulletins, reçus, attestations et certificats ont un
identifiant unique et un mécanisme de vérification qui ne divulgue pas
de données superflues.

**Règles :** brouillon marqué ; correction versionnée ; invalidation
vérifiable ; accès selon tenant, rôle et rattachement ; QR non
prédictible sans données personnelles en clair.

**Cycle :** demande → génération → contrôle → émission → distribution →
vérification → remplacement/révocation → archivage.

**Acceptation :** document falsifié ou révoqué détectable.

## DM-045 --- Messagerie institutionnelle

**Statut : recommandation à ratifier.**

**Décision :** une communication est liée à un établissement, une
audience, une finalité et un auteur.

**Règles :** audience vérifiée ; messages de masse approuvés ;
distinguer envoi, livraison et lecture ; pièces jointes protégées ;
versions conservées.

**Cycle :** brouillon → revue → approbation → planification → diffusion
→ suivi → correction/retrait → archivage.

**Acceptation :** aucun destinataire hors audience autorisée.

------------------------------------------------------------------------

# 7. Extensions et intégrations

## DM-046 --- Ressources humaines et paie

**Statut : recommandation à ratifier.**

**Décision :** dossier RH, compte utilisateur, affectation, préparation
de paie et paiement effectif sont distincts.

**Règles :** accès RH limité ; contrats et fonctions datés ; calcul de
paie explicable et versionné ; validation de paie distincte du paiement
exécuté.

**Cycle :** dossier/recrutement → vérification → contrat actif →
affectation → variables de paie → calcul → contrôle → approbation →
paiement → clôture période → fin contrat/archivage.

**Acceptation :** calcul reproductible et statut de paiement confirmé.

## DM-047 --- Bibliothèque, inventaire, transport et internat

**Statut : recommandation à ratifier.**

**Décision :** ces modules sont optionnels par établissement et chacun
possède son propre cycle.

**Règles :** bibliothèque : exemplaire → prêt → échéance → retour/perte
→ clôture ; inventaire : article → entrée/sortie/transfert → comptage →
écart → régularisation ; transport : ligne/arrêt → affectation → suivi →
incident → fin ; internat : capacité/chambre → affectation → séjour →
sortie → clôture. Les frais éventuels sont explicitement configurés.

**Cycle commun :** configuration → ressources → contrôle capacité →
affectation/opération → suivi → exception → clôture → historique.

**Acceptation :** mouvements traçables, capacité contrôlée et
désactivation sans perte d'historique.

## DM-048 --- Santé scolaire et données sensibles

**Statut : recommandation à ratifier et revue juridique obligatoire.**

**Décision :** les données de santé sont isolées, minimisées et
accessibles uniquement pour une finalité autorisée.

**Règles :** définir base juridique/consentement applicable,
responsable, accès et rétention ; pas de visibilité automatique aux
enseignants ou portails ordinaires ; urgences avec protocole dédié ;
exports minimisés.

**Cycle :** besoin → autorisation applicable → collecte minimale → accès
habilité → mise à jour → partage justifié → rétention → archivage/purge
selon droit.

**Acceptation :** consultation sensible auditée et tests d'accès
négatifs.

## DM-049 --- API, imports/exports, webhooks et interopérabilité

**Statut : recommandation à ratifier.**

**Décision :** toute intégration passe par un contrat versionné,
authentifié, limité et observable, sans contourner les règles métier.

**Règles :** API versionnée et scopes minimaux ; import avec
prévisualisation, validation et détection doublons ; export limité et
journalisé ; webhooks signés, horodatés, idempotents ; connecteurs
découplés ; OneRoster/LTI/Ed-Fi étudiés selon besoin et profil
réellement supporté ; dépréciation annoncée.

**Cycle :** besoin → contrat → revue sécurité/données → approbation →
configuration → test → activation → supervision → rotation/révocation →
dépréciation → retrait.

**Acceptation :** tests scopes, signature, rejeu, doublons, panne
fournisseur et versions incompatibles.

## DM-050 --- Analytics, IA, offline et automatisations

**Statut : recommandation à ratifier.**

**Décision :** ces capacités assistent les opérations, mais restent
soumises aux autorisations, à la qualité des données, à l'explicabilité
et au contrôle humain.

**Règles :** KPI définis (formule, périmètre, fraîcheur, propriétaire) ;
provisoire/officiel distingués ; IA ne valide jamais seule admission,
note, délibération, promotion, sanction, remise ou paiement ; sorties IA
non fiables par défaut ; minimisation des données ; offline avec
identifiant unique, horodatages distincts et résolution explicite des
conflits ; automatisation arrêtée/reprise sans double effet.

**Cycle :** besoin → définition → revue risque/données → validation →
pilote → contrôle humain → activation limitée → mesure
qualité/coût/latence/biais → suspension/amélioration → retrait.

**Acceptation :** KPI reproductible ; conflit offline non écrasé ;
action IA sensible approuvée par humain ; automatisation idempotente et
désactivable.

------------------------------------------------------------------------

# 8. Invariants de bout en bout intermodules

1.  Admission → inscription → affectation : admission acceptée ne vaut
    pas inscription ; inscription validée précède l'affectation
    régulière.
2.  Affectation → cours → présence → évaluation : les opérations
    utilisent l'affectation valide à la date concernée.
3.  Évaluation → note → calcul → clôture → délibération : aucune donnée
    provisoire ne devient décision officielle.
4.  Délibération → promotion → année suivante : promotion fondée sur
    décision validée et configuration cible.
5.  Barème → obligation → échéance → paiement → reçu → comptabilité :
    chaque étape conserve l'origine et évite les doublons.
6.  Paiement externe → callback → vérification → imputation : callback
    répété sans double effet.
7.  Sortie élève → révocation accès → documents → archives : la sortie
    ne détruit pas les preuves.
8.  Lien parent → portail → notification : chaque accès vérifie le
    rattachement actif.
9.  Affectation enseignant → portail → saisie → soumission → retrait :
    droits alignés sur l'affectation, auteur conservé.
10. Configuration → calcul → bulletin : version de configuration figée
    et consultable.
11. API/import → validation métier → événement → notification : aucune
    donnée externe n'est officielle avant contrôle.
12. Offline → synchronisation → conflit : aucun écrasement silencieux
    d'une donnée validée.
13. IA → recommandation → approbation humaine → action : l'IA ne
    contourne jamais les permissions serveur.
14. Incident → restauration → rapprochement : intégrité des données,
    événements, documents et finances vérifiée.

------------------------------------------------------------------------

# 9. Cycle obligatoire de remise à niveau de chaque fonctionnalité existante

Pour chaque fonctionnalité déjà présente dans EduNova :

1.  Inventorier interfaces, routes API, services, dépôts, données,
    rôles, événements, documents et intégrations.
2.  Identifier son propriétaire métier et sa source de vérité.
3.  Décrire le parcours actuel réel, sans supposer que le code reflète
    le métier.
4.  Décrire le parcours cible et les écarts.
5.  Définir états, transitions, préconditions, postconditions, acteurs