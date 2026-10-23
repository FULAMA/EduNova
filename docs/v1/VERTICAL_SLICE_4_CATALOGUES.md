# Vertical slice 4 — catalogues académiques

## Livré

- Le catalogue de matières réutilise l'entité `Subject` existante (`name`, `code`, `coefficient`, `active`) et l'association `ClassSubject` existante.
- Les administrateurs peuvent lister, rechercher par nom, créer et renommer une matière / modifier son code. Le coefficient est conservé lors d'une modification, car les contrats ne définissent pas sa politique d'évolution. La création respecte l'invariant déjà défini par `Subject` : coefficient strictement positif.
- Tous les accès au catalogue filtrent le tenant issu du JWT et exigent un membership actif de rôle `ADMIN`.
- Les périodes sont consultables par établissement, et les périodes d'un dossier élève retournent désormais `{id, name}`. L'écran d'élève et le tableau de résultats affichent les libellés disponibles. Les UUID restent les clés utilisées pour les requêtes.
- Le catalogue d'une période contient `name`, `start_date` et `end_date`, conformes à l'entité existante. Aucune création/modification/suppression de période n'est exposée.
- Les références historiques sans libellé renvoient `name: null` et sont présentées comme « Période non renseignée » / « Libellé de matière indisponible », sans nom fabriqué.

## Migrations et stockage

La migration additive `017` ajoute le catalogue tenant-scopé `academic_periods` et des index de lecture aux tables existantes. Elle n'infère pas de libellé depuis les UUID historiques et ne touche pas aux dossiers ou résultats existants. La base `edunova.db` n'a pas été utilisée pour exécuter cette migration. Initialisation et tests se font via `SQLiteDatabase.initialize()` sur des fichiers temporaires.

Pour des périodes existantes, un opérateur doit fournir le libellé et les dates de l'établissement puis insérer ces données avec le même `tenant_id` et l'UUID déjà référencé par les dossiers. Cette livraison n'ajoute volontairement aucune association calendaire aux anciennes données ni contrainte de clé étrangère qui pourrait rendre inaccessibles des dossiers historiques incohérents.

## Contrats HTTP

- `GET /academic-catalogues/subjects?search=...`
- `POST /academic-catalogues/subjects` avec `{name, code, coefficient}`
- `PUT /academic-catalogues/subjects/{id}` avec `{name, code}`; coefficient conservé
- `GET /academic-catalogues/periods`
- `GET /academic-records/students/{id}/periods` retourne `{id, name}`
- `GET /academic-records/{student_id}/{period_id}` ajoute `academic_period_name` et `subject_name` aux UUID techniques existants.

## Décisions métier encore requises

Avant d'exposer une gestion des périodes, préciser : chevauchement permis ou interdit, cardinalité des périodes ouvertes, modèle année scolaire/calendrier, possibilité de modifier une période avec des dossiers liés, suppression/désactivation, et autorité chargée de ces décisions. Il faut aussi définir les règles d'évolution des coefficients des matières et si le code est modifiable après association à des classes ou résultats. En attendant, l'API expose uniquement la lecture des périodes et conserve le coefficient existant sur modification d'une matière.

## Essai local

Dans `frontend` : `npm run dev`. `create_app()` sans conteneur utilise par défaut une base SQLite en mémoire. Pour une base fichier isolée, construire explicitement `ApplicationContainer(database_path=<chemin-temporaire>)` puis passer ce conteneur à `create_app(container)` ; définir seulement `EDUNOVA_DATABASE_PATH` ne remplace pas le paramètre mémoire par défaut du factory. Connecter un administrateur, ouvrir « Configuration académique » pour gérer les matières et voir les périodes, puis ouvrir une fiche élève ayant un dossier pour contrôler les libellés. Ne pas lancer l'application avec `edunova.db` tant que son schéma historique n'a pas fait l'objet d'une procédure de migration séparée.
