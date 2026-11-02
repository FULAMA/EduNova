# Audit préalable — intégration de Rust et C dans EduNova

**Statut :** proposition technique à examiner — aucune décision d'implémentation native n'est encore adoptée.  
**Périmètre :** sécurité, performances et fiabilité, sans changement du comportement métier ni de la base de données.

## 1. Résumé exécutif

EduNova utilise actuellement Python/FastAPI comme backend applicatif. Le fichier `pyproject.toml` définit un projet Python (>=3.13,<3.14) avec setuptools et ses dépendances applicatives ; il ne déclare actuellement ni workspace Cargo, ni compilation C, ni chaîne de construction native.

L'intégration de Rust et C doit donc être introduite progressivement, dans une branche isolée, avec une CI capable de compiler et tester les composants natifs. Il ne faut pas déplacer du code métier vers un langage natif sans mesurer un problème réel ou identifier une exigence de sécurité précise.

**Orientation proposée :**
- Python reste responsable de l'API, des autorisations, de l'orchestration et de la persistance.
- Rust est le choix par défaut pour un nouveau composant natif lorsque le besoin est démontré.
- C est réservé aux bibliothèques existantes, aux interfaces système ou à un besoin bas niveau justifié.
- Toute frontière FFI est traitée comme une frontière de sécurité : entrées validées, contrats ABI documentés, gestion explicite des erreurs et tests d'intégration.
- Aucun composant natif ne contourne les contrôles de tenant, les autorisations métier, les transactions ou les règles d'audit du backend.

## 2. Constats vérifiables à partir du dépôt

1. Le projet Python exige `>=3.13,<3.14` et utilise setuptools comme backend de construction.
2. Les dépendances de production actuelles incluent FastAPI, Pydantic, PyJWT, PyOTP, argon2-cffi, google-auth et fpdf2.
3. Le registre métier contient des décisions validées sur les calculs scolaires :
   - la formule de moyenne générale est configurable par établissement, versionnée et traçable ;
   - une note manquante est distincte d'un zéro ;
   - les résultats historiques ne sont pas réinterprétés silencieusement ;
   - les modifications de politique ne provoquent pas de recalcul rétroactif automatique ;
   - les résultats officiels reposent sur les conditions de complétude et les validations applicables.
4. Les décisions du projet imposent des tests de sécurité, d'isolation multi-tenant, de non-régression et des optimisations fondées sur des mesures.
5. Le dépôt ne déclare pas encore, dans son manifeste Python, une chaîne de compilation Rust/C.

**Limite de l'audit :** ces constats documentaires ne prouvent ni qu'un goulot d'étranglement existe, ni qu'un calcul précis est actuellement erroné. Un audit du code de calcul et des mesures de référence reste nécessaire avant de choisir le premier composant de production.

## 3. Candidats à évaluer

| Candidat | Valeur potentielle | Risque principal | Décision actuelle |
|---|---|---|---|
| Noyau pur de calcul académique | Résultats déterministes et comparaison différentielle entre implémentations | Divergence avec les règles métier, arrondis ou traitement incorrect des notes manquantes | Candidat pilote à auditer, pas encore autorisé pour la production |
| Import en lots de données scolaires | Débit et validation de grands fichiers | Rejets incohérents, consommation mémoire et erreurs de provenance | À évaluer après mesure |
| Traitement parallèle de rapports | Réduction du temps de génération en volume | Charge CPU/mémoire et effets sur la disponibilité | À mesurer avant décision |
| Bibliothèques C existantes | Réutilisation d'implémentations éprouvées ou intégration système | Surface mémoire non sûre et maintenance de dépendances natives | Seulement si un besoin concret est identifié |
| Cryptographie native personnalisée | Aucun avantage présumé | Risque élevé d'erreurs de conception | À éviter ; préférer des bibliothèques maintenues et éprouvées |

## 4. Contrat de sécurité pour les composants natifs

Chaque composant natif devra respecter les exigences suivantes avant toute intégration :

1. **Entrées bornées et validées** : limites explicites de taille, types, plages et encodages.
2. **Contrat stable** : entrées, sorties, erreurs et version de l'interface documentées.
3. **Gestion mémoire claire** : préciser qui alloue, qui libère et pendant combien de temps les données restent valides.
4. **FFI minimale** : exposer uniquement les fonctions indispensables ; éviter d'exposer des pointeurs ou des structures internes instables.
5. **Aucune confiance implicite** : les sorties natives sont validées par le backend avant persistance ou publication.
6. **Isolation conservée** : le tenant et l'acteur autorisé sont déterminés et contrôlés côté serveur ; le composant natif ne décide pas des permissions.
7. **Erreurs sûres** : pas de secret ni de donnée scolaire sensible dans les messages d'erreur ou les journaux.
8. **Dépendances contrôlées** : versions verrouillées, analyse des vulnérabilités et inventaire des bibliothèques.
9. **Pas de code `unsafe` sans justification** dans Rust ; toute zone `unsafe` doit être minimale, documentée et testée.
10. **Pas de changement automatique de schéma** : aucun composant natif ne crée ou ne migre la base de données.

## 5. Stratégie d'intégration

L'ordre de préférence est :

1. Garder le composant dans Python si sa complexité et ses performances sont acceptables.
2. Si un besoin est démontré, tester une bibliothèque Rust appelée par une interface étroite.
3. Préférer un processus séparé lorsque l'isolation opérationnelle ou la simplicité de déploiement l'emporte sur le coût de communication.
4. Employer une ABI C/FFI uniquement lorsque l'interopérabilité ou les contraintes de performance le justifient.
5. Ajouter C uniquement pour un besoin bas niveau précis ou pour réutiliser une bibliothèque existante ; ne pas créer une couche C artificielle entre Python et Rust.

Le choix entre extension native et processus séparé doit être décidé à partir du cas d'usage, des plateformes de déploiement, de la charge et des exigences d'isolation.

## 6. Plan de validation du premier pilote

Avant de remplacer une implémentation existante :

- Identifier le code Python exact et les règles métier associées.
- Établir des cas de référence et des mesures de performance reproductibles.
- Définir les invariants : mêmes entrées valides, mêmes résultats, mêmes règles d'arrondi et mêmes erreurs métier attendues.
- Couvrir les limites, valeurs manquantes, valeurs extrêmes, données invalides et règles versionnées.
- Exécuter des tests différentiels Python/Rust sur des jeux synthétiques et anonymisés.
- Mesurer latence, débit et mémoire ; ne retenir Rust que si le bénéfice est démontré ou si une exigence de sûreté le justifie.
- Vérifier l'absence de régression dans les tests backend existants.
- Ajouter à la CI la compilation, les tests Rust et les contrôles de qualité/sécurité nécessaires.
- Faire passer le composant par revue humaine et PR distincte ; aucune fusion automatique.

Pour le calcul académique, le pilote doit rester une fonction pure : aucune requête SQL, aucun accès réseau, aucune autorisation, aucune écriture d'audit et aucune mutation de données. Python reste responsable de charger la politique versionnée et de persister le résultat avec son contexte.

## 7. Portée de cette proposition

Ce document ne :
- modifie aucun fichier de production ;
- ajoute aucune dépendance ou chaîne de compilation ;
- crée aucune migration ;
- ne change aucune règle de calcul ou d'autorisation ;
- n'affirme aucun gain de performance non mesuré ;
- n'autorise pas la fusion de cette proposition.

**Étape suivante proposée :** auditer les implémentations actuelles du calcul des moyennes et de la délibération, leurs tests et leurs contrats de versionnement. Choisir ensuite un seul pilote sur la base des preuves obtenues.


## 8. Résultats de l'inspection ciblée du code Python

Les fichiers suivants ont été inspectés sur `main` : `SubjectAverageCalculator`, `AcademicAverageCalculator`, `AcademicPolicy`, `DeliberationEngine`, `Score`, `SubjectResult`, `Deliberation` et les tests unitaires associés.

### Calcul de moyenne par matière

`SubjectAverageCalculator.calculate` :
- matérialise les notes en liste ;
- rejette une liste vide ;
- normalise chaque note via un `ScoreConverter` injecté ;
- calcule une moyenne pondérée avec des `float` ;
- rejette une somme de coefficients inférieure ou égale à zéro.

Les tests couvrent la moyenne pondérée, la liste vide, une note unique, la normalisation d'une échelle et l'injection du convertisseur. Les tests inspectés ne démontrent pas encore une couverture complète des valeurs extrêmes, des entrées non finies et de la reproductibilité sur de grands lots.

### Calcul de moyenne générale

`AcademicAverageCalculator.calculate` utilise `math.fsum` pour sommer les coefficients et les moyennes pondérées. En cas de dépassement numérique, il tente un calcul avec coefficients mis à l'échelle. Les résultats par matière valident déjà une moyenne finie entre 0 et 20 et un coefficient fini strictement positif.

Les tests inspectés couvrent le calcul pondéré, la liste vide, une matière et l'effet du coefficient. Aucun benchmark de référence n'a été identifié dans les fichiers inspectés. Rien ne prouve actuellement que ce calcul soit un goulot d'étranglement.

### Délibération

`DeliberationEngine` applique une `AcademicPolicy` fournie par injection et produit `ADMITTED`, `CONDITIONAL` ou `FAILED`. Les tests inspectés couvrent les trois décisions. La persistance et la validation versionnée se situent dans les couches applicatives/infrastructure ; elles doivent rester hors du composant natif éventuel.

### Points à vérifier avant un pilote

- La formule métier est versionnée au niveau du dossier/calcul, mais le service de moyenne générale inspecté reçoit seulement les résultats par matière ; il faut tracer le chemin d'injection de la politique et confirmer où la version exacte est attachée au calcul.
- Les calculs emploient des nombres flottants. Il faut documenter les attentes exactes d'arrondi et de comparaison avant toute réimplémentation, sans changer le comportement par accident.
- `AcademicPolicy.round_average` utilise l'arrondi natif Python `round`; les tests couvrent un cas simple mais pas les cas limites de représentation binaire ou de demi-valeurs.
- Les tests actuels donnent des exemples métier utiles, mais il faut des tests différentiels, des cas limites et un benchmark reproductible avant de conclure qu'une implémentation Rust est plus fiable ou plus rapide.
- Le moteur de délibération est petit et lisible ; une réécriture native n'est pas justifiée à ce stade sur la seule base de sa complexité apparente.

## 9. Conclusion de l'audit et choix du pilote

**Choix recommandé pour l'étape expérimentale :** isoler le calcul pur de moyenne générale comme candidat de preuve de concept, sans l'activer en production. Il est déterministe à contrat égal, reçoit des résultats déjà validés et permet une comparaison différentielle directe avec Python.

Avant de coder ce pilote :
1. renforcer et figer les tests de référence Python ;
2. clarifier la politique d'arrondi et les invariants attendus ;
3. mesurer des tailles de lots réalistes avec un benchmark reproductible ;
4. implémenter le prototype Rust uniquement si la preuve de concept sert à valider l'intégration ou si les mesures révèlent un gain utile ;
5. comparer chaque résultat Rust au résultat Python et bloquer tout écart inexpliqué.

Le moteur de délibération n'est pas le premier candidat : sa logique est courte et son comportement est mieux conservé dans Python tant qu'aucune raison mesurée ne justifie de le déplacer. C ne fait pas partie du premier pilote ; il sera introduit seulement pour un besoin d'interopérabilité ou bas niveau concret.
