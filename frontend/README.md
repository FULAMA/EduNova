# Parcours élèves et dossiers académiques

## Contrats disponibles

- `GET /students` liste les élèves visibles pour le tenant authentifié.
- `GET /students/{student_id}` retourne la fiche d’un élève.
- `GET /academic-records/students/{student_id}/periods` retourne les UUID de périodes ayant un dossier pour cet élève.
- `GET /academic-records/{student_id}/{academic_period_id}` retourne les moyennes, crédits, matières échouées et résultats par matière.

Ces lectures exigent un membership actif `ADMIN`. Le backend dérive le tenant du jeton et filtre les requêtes avec ce contexte. Un ID de période est affiché tel que persisté, car aucune table de libellés de périodes n’existe. Les matières sont également identifiées par UUID dans le contrat actuel; aucune étiquette n’est inventée. Les moyennes et coefficients sont présentés avec les unités du contrat existant.

## Lancement local

Dans un premier terminal, utiliser une base temporaire dédiée pour les essais, activer le seed uniquement en développement avec `EDUNOVA_DEV_SEED=true` et définir `EDUNOVA_DEV_SEED_PASSWORD` dans l’environnement. Démarrer l’API avec la fabrique actuelle :

```powershell
uvicorn src.presentation.api.app:create_app --factory --reload
```

Le seed est refusé en production. La base locale `edunova.db` a un historique de migrations vide et un schéma qui ne correspond pas entièrement aux migrations; ne pas l’utiliser pour ces essais et ne pas y lancer de migration.

Dans un second terminal :

```powershell
cd frontend
npm run dev
```

Se connecter avec le compte de développement du seed, ouvrir **Élèves**, choisir un élève puis consulter **Dossiers académiques**. Sélectionner une période pour charger ses résultats. Si aucun dossier n’existe, la fiche l’indique explicitement.

Les commandes `npm test`, `npm run lint` et `npm run build` exécutent respectivement les tests frontend, Oxlint et le build TypeScript/Vite.

## Diagnostic en lecture seule de la base locale

La configuration résout `edunova.db` en chemin relatif. La table `schema_migrations` existe, mais aucune version n’y est enregistrée. Le schéma observé contient 17 tables; `students` possède `student_number` et `date_of_birth`, contrairement au schéma des migrations consultées qui définissent `first_name`, `last_name` et `email`. Les tables de dossiers académiques et de résultats possèdent `tenant_id`, mais `academic_periods` n’existe pas; `students` et `student_academic_records` n’ont pas de clés étrangères déclarées. La table `subject_results` a des clés étrangères vers le dossier, mais pas de clé tenant composite.

La colonne `students.tenant_id` ne suffit donc pas à établir que la migration 009 ou les migrations suivantes ont été appliquées. L’origine de ce schéma est indéterminée. Avant de réutiliser cette base, comparer une sauvegarde à l’historique attendu et établir une procédure de reprise avec l’opérateur. Aucun changement n’a été effectué sur cette base pendant cette mission.
