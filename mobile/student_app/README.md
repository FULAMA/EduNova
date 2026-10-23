# EduNova Student

Application Flutter unique pour les roles eleve, parent et professeur.

Le role est resolu depuis `GET /auth/me`. Le module eleve est actif ; les modules parent et professeur restent explicitement indisponibles tant que leurs contrats backend n'existent pas.

## Contrats consommes

- `POST /auth/login` et `POST /auth/2fa/login`
- `GET /me/student`
- `GET /me/student/academic-periods`
- `GET /me/student/academic-records/{academic_period_id}`
- `GET /me/student/attendance/{academic_period_id}`
- `GET /report-cards`
- `GET /report-cards/{report_card_id}/pdf`
- `GET /auth/me` pour la resolution du role authentifie

Les permissions et l'isolation tenant restent celles du backend. Le client ne transmet pas de `student_id` pour choisir l'identite connectee.

## Execution locale

Sur Android Emulator, l'API locale de l'hote est `http://10.0.2.2:8017` :

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8017
```

Sur un appareil physique, utiliser une URL de test HTTPS ou une adresse reseau explicitement autorisee. Ne pas exposer l'API temporaire ReportCard.

## Limites de cette tranche

- `MemorySessionStore` est un adaptateur de developpement et de test uniquement.
- Avant distribution, il doit etre remplace par un stockage securise Android/iOS, sans journaliser les jetons.
- Les PDF sont lus en memoire et ne sont pas persistes localement.
- Les tests Flutter et la compilation Android doivent etre executes lorsque le SDK Flutter est disponible sans lockfile bloque.
