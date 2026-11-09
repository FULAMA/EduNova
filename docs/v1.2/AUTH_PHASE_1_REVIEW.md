# REVUE TECHNIQUE INDÉPENDANTE — AUTH-HARDENING V1.2 (PHASE 1)

**Date :** 2026-11-08  
**Réviseur :** Antigravity (Revue technique indépendante)  
**Branche Git :** `fix/mypy-test-double-contracts`  
**Objet de la revue :** Audit d'ingénierie et de sécurité approfondi des modifications apportées lors de la Phase 1 (Anti-énumération, Rate Limiting, Protection TOTP).  
**Décision globale :** **ACCEPTED_WITH_RESERVATIONS**  
**Bases de données persistantes :** `edunova.db` et `edunova_dev.db` préservées (aucun reset, aucun clean, aucune écriture non autorisée).

---

## 1. Synthèse Exécutive de la Revue

La Phase 1 a introduit des avancées significatives pour la sécurité d'EduNova, notamment :
- L'égalisation du temps d'exécution sur `/auth/login` via un calcul Argon2id factice (`_DUMMY_ARGON2_HASH`) ;
- L'unification des messages d'erreur empêchant l'énumération publique des comptes ;
- Un port d'abstraction `RateLimiter` propre à la Clean Architecture avec implémentation thread-safe `InMemoryRateLimiter` ;
- Un double cloisonnement des quotas (par IP et par couple IP/compte) empêchant un attaquant de bloquer le compte d'une victime ;
- La limitation stricte à 3 tentatives de validation par session 2FA et la consommation à usage unique du jeton JWT 2FA.

Cependant, l'examen technique indépendant met en évidence **deux réserves techniques majeures** qui empêchent une acceptation inconditionnelle sans réserves :
1. **Rate Limiting strictement local au worker :** L'implémentation en mémoire n'est pas distribuée. En environnement multi-workers ou multi-instances, les quotas sont multipliés par le nombre de workers. De plus, la confiance accordée à l'en-tête `X-Forwarded-For` sans validation de proxy de confiance expose à un contournement d'IP.
2. **Anti-rejeu du code TOTP manquant (RFC 6238) :** Si l'anti-rejeu du jeton JWT (`two_factor_token`) est parfaitement effectif, le système ne mémorise pas le dernier pas de temps (time-step) TOTP validé. Deux sessions 2FA distinctes initiées pour le même utilisateur peuvent ainsi être validées avec le même code à 6 chiffres dans l'intervalle de 30 secondes.

---

## 2. Évaluation Détaillée par Domaine

### 2.1 Rate Limiting et Gestion des Tentatives

| Critère | Constat Technique | Risque / Statut | Recommandation |
|---|---|---|---|
| **Interface `RateLimiter`** | Propre, découplée du stockage (`check_and_record`, `is_limited`, `reset`). Respecte le principe d'inversion des dépendances (DIP). | **VERIFIED** | Maintenir l'interface intacte pour les futurs adaptateurs (Redis). |
| **Thread-Safety** | `InMemoryRateLimiter` utilise un `threading.Lock()` englobant toutes les manipulations de compteurs. Testé sous 100 threads simultanés. | **VERIFIED** | Conforme pour un usage multi-thread dans un même processus. |
| **Comportement Multi-Workers** | L'état `self._hits` est stocké dans la RAM du processus Python. Chaque worker (ex: Uvicorn / Gunicorn avec 4 workers) dispose de son propre dictionnaire indépendant. | **PARTIAL** | Documenter explicitement que sous $N$ workers, la limite réelle perçue par un attaquant est de $N \times \text{limite}$. Pour la production, implémenter un `RedisRateLimiter`. |
| **Confiance `X-Forwarded-For`** | `get_client_ip()` lit directement le premier segment de `X-Forwarded-For` sans vérifier si la requête provient d'un reverse proxy de confiance. | **VULNERABLE** | Si l'API est exposée directement à Internet sans reverse proxy filtrant, un client peut forger `X-Forwarded-For: <ip_aleatoire>` à chaque requête et contourner le rate limiting IP. Configurer une liste blanche de reverse proxies (ex: `--forwarded-allow-ips`). |
| **Gestion de la Mémoire (RAM)** | Les listes de timestamps expirés sont filtrées, mais les clés du dictionnaire `self._hits` ne sont jamais supprimées sauf appel explicite à `reset()`. | **PARTIAL** | Sous une attaque par dictionnaire avec des millions d'emails ou d'IPs forgées, `self._hits` accumule des millions d'entrées vides (`key: []`). Supprimer la clé du dictionnaire lorsque la liste de timestamps devient vide. |
| **Disponibilité du Stockage** | Comme le stockage est en mémoire vive du processus, il ne souffre pas de pannes réseau. Si une bascule vers Redis a lieu en Phase 2/3, une politique de "fail-open" ou "fail-closed" devra être définie. | **VERIFIED** | Prévu pour Redis ultérieurement. |

---

### 2.2 Réinitialisation des Compteurs et Résistance au Déni de Service (DoS)

| Critère | Constat Technique | Risque / Statut | Analyse de Sécurité |
|---|---|---|---|
| **Compteurs Réinitialisés** | Seul `login:target:{client_ip}:{normalized_email}` est supprimé lors d'une connexion réussie. | **VERIFIED** | Comportement optimal : l'utilisateur légitime retrouve un quota complet immédiatement après saisie du bon mot de passe. |
| **Maintien du Quota IP** | `login:ip:{client_ip}` n'est **jamais** réinitialisé lors d'un succès. | **VERIFIED** | Empêche un attaquant de réinitialiser son quota d'IP en se connectant à un compte "leurre" qu'il contrôle. |
| **Risque de DoS sur Victime** | Le compteur ciblé incorpore l'IP du client (`login:target:{client_ip}:{email}`). | **VERIFIED** | Un attaquant depuis l'IP $A$ bloqué après 5 essais sur `admin@edunova.com` n'affecte en rien l'administrateur légitime se connectant depuis l'IP $B$. |
| **Attaque Distribuée (Botnet)** | Si un attaquant utilise 10 000 adresses IP distinctes (1 essai par IP), ni le quota par IP ni le quota par couple (IP, email) n'est déclenché. | **PARTIAL** | Limite inhérente au rate limiting sans verrouillage global de compte. L'absence de verrouillage global de compte est un choix de conception délibéré et validé pour éviter le déni de service de compte (Account Lockout DoS). Un composant WAF / CAPTCHA périphérique est la réponse standard pour ce risque. |

---

### 2.3 Protection TOTP : Anti-Rejeu JWT vs Anti-Rejeu Code TOTP

Une distinction fondamentale doit être opérée entre l'anti-rejeu du token d'attente JWT et l'anti-rejeu du code TOTP lui-même :

| Composant | Comportement Actuel | Risque / Statut | Preuve Technique |
|---|---|---|---|
| **A. Anti-rejeu du jeton JWT 2FA (`jti`)** | Dès validation réussie, le `token_id` (`jti`) est enregistré dans `f"2fa:consumed:{token_id}"`. Toute soumission ultérieure du même jeton lève `ValueError("Token 2FA deja consomme.")`. | **VERIFIED** | Testé avec succès dans `test_verify_login_two_factor_protection.py::test_totp_prevents_token_replay_after_success`. |
| **B. Plafond d'essais sur session 2FA** | Après 3 codes incorrects sur un jeton donné, le 4ème essai est bloqué avec `"Nombre maximal de tentatives 2FA depasse."` (HTTP 429). | **VERIFIED** | Testé dans `test_verify_login_two_factor_protection.py::test_totp_blocks_after_three_failed_attempts`. |
| **C. Anti-rejeu du code TOTP (RFC 6238 time-step)** | Le système **ne stocke pas** le pas de temps TOTP (`last_time_step`) pour l'utilisateur. Si deux sessions 2FA distinctes sont créées (ex: deux onglets ou interception réseau du mot de passe), le **même code à 6 chiffres peut être validé deux fois** dans sa fenêtre de 30 secondes. | **VULNERABLE** | Prouvé par exécution directe : deux sessions avec deux jetons distincts acceptent le même code TOTP dans la même fenêtre de 30 secondes. |

**Recommandation pour la Phase 2 :**  
Conformément à la RFC 6238 Section 5.2 (*"The server MUST NOT accept the OTP more than once for a given user within the validity period"*), enregistrer le dernier pas de temps validé :
```python
# Exemple de garde-fou à intégrer en Phase 2 :
time_step = int(time.time() / 30)
if rate_limiter.is_limited(f"2fa:user_step:{user.id}:{time_step}", limit=1, window_seconds=60):
    raise ValueError("Code 2FA deja utilise dans cette fenetre temporelle.")
rate_limiter.check_and_record(f"2fa:user_step:{user.id}:{time_step}", limit=1, window_seconds=60)
```

---

### 2.4 Anti-Énumération et Protection des Informations Sensibles

| Critère | Constat Technique | Statut | Preuve Technique |
|---|---|---|---|
| **Équivalence des Messages Publics** | Les comptes inexistants, inactifs, désactivés ou les mots de passe erronés renvoient tous strictement HTTP 401 avec `"Identifiants invalides."`. | **VERIFIED** | `LoginUser.execute()` unifie les rejets sous la même exception `ValueError("Identifiants invalides.")`. |
| **Calcul Argon2 factice** | Si `user is None`, `self._password_hasher.verify(password, self._dummy_password_hash)` est exécuté. | **VERIFIED** | Vérifié avec l'espion `SpyPasswordHasher` dans `test_login_user_timing_anti_enumeration.py`. |
| **Paramètres du hash factice** | `_DUMMY_ARGON2_HASH` utilise `$argon2id$v=19$m=65536,t=3,p=4$`, identique aux paramètres par défaut de `Argon2PasswordHasher`. | **VERIFIED** | Consommation CPU et mémoire strictement équivalente. |
| **Garantie temporelle réaliste** | L'écart macroscopique de 60ms est neutralisé. Des variations infimes de microsecondes (requête SQLite retournant 0 ligne vs 1 ligne) subsistent, ce qui est normal et documenté. | **VERIFIED** | Aucune allégation abusive de "temps strictement constant" dans la documentation. |
| **Fuites de secrets dans les logs** | Aucun mot de passe, hash ni secret 2FA n'est tracé dans les logs ou les détails d'exception HTTP 429 / 401. | **VERIFIED** | Audit de code de `routes/auth.py`. |

---

## 3. Revue des Preuves de Tests

| Suite de Tests | Localisation | Nombre de Tests | Type | Exécution Réelle |
|---|---|---|---|---|
| **Rate Limiter Mémoire** | `tests/unit/identity/infrastructure/security/test_in_memory_rate_limiter.py` | 8 tests | Unitaire / Multi-thread | **PASS (100%)** |
| **Anti-Énumération & Timing** | `tests/unit/identity/application/use_cases/test_login_user_timing_anti_enumeration.py` | 3 tests | Unitaire (Spy) | **PASS (100%)** |
| **Protection 2FA TOTP** | `tests/unit/identity/application/use_cases/test_verify_login_two_factor_protection.py` | 4 tests | Unitaire | **PASS (100%)** |
| **Routes HTTP & Codes 429** | `tests/unit/presentation/api/routes/test_auth_rate_limiting.py` | 5 tests | Intégration Route | **PASS (100%)** |
| **Suite Complète Backend** | `tests/unit/` | 1052 tests | Unitaire / Intégration | **PASS (100%) en 26.62s** |
| **Suite Complète Frontend** | `frontend/src/` | 170 tests (36 fichiers) | Vitest / JSDOM | **PASS (100%) en 35.29s** |

---

## 4. État des Comptes de Développement dans EduNova

Dans le cadre de cette revue, l'environnement de données a été inspecté :

1. **État actuel de `edunova.db` :**
   - La base SQLite `edunova.db` existe (430 Ko) et contient le schéma de 38 migrations canoniques.
   - Requête en lecture seule (`file:edunova.db?mode=ro`) :
     - Table `users` : **0 compte**
     - Table `memberships` : **0 adhésion**
     - Table `tenants` : **0 établissement**
   - La base `edunova_dev.db` n'existe pas.

2. **Règles de protection respectées :**
   - Conformément à la règle 5 ("N'interviens jamais sur `edunova.db` ou `edunova_dev.db` sans autorisation") et à la règle 6 ("Ne modifie aucune donnée de production"), **aucune insertion n'a été effectuée dans `edunova.db` sans ordre explicite**.

3. **Mécanisme standard de génération de compte de test :**
   EduNova dispose du module officiel `src/infrastructure/bootstrap/development_seed.py` qui génère de manière reproductible un compte `ADMIN` sécurisé avec hachage Argon2id :
   - **Établissement (Tenant) :** `EduNova Development` (UUID: `00000000-0000-0000-0000-000000000001`)
   - **Email :** `admin@edunova.com` (UUID: `00000000-0000-0000-0000-000000000002`)
   - **Rôle :** `ADMIN` (Membership UUID: `00000000-0000-0000-0000-000000000003`)
   - **Mot de passe initial proposé :** `EduNova@Dev2026!Admin` (ou configuré via `EDUNOVA_DEV_SEED_PASSWORD`)
   - **Environnement concerné :** `development` ou `test` uniquement.

Dès que vous en donnerez l'autorisation formelle, ce bootstrap officiel pourra être appliqué pour initialiser le compte ADMIN de développement.

---

## 5. Décision Finale

### Décision : **ACCEPTED_WITH_RESERVATIONS**

#### Justification :
La Phase 1 remplit l'ensemble de ses objectifs fondamentaux :
- L'attaque par force brute sur mot de passe et 2FA depuis une même IP est neutralisée (HTTP 429).
- L'énumération publique des comptes par analyse temporelle ou message d'erreur est résolue.
- Le rejeu du jeton d'attente 2FA est impossible.
- La base de code conserve 100% de succès aux tests (1052 tests backend, 170 tests frontend, 0 erreur Ruff, 0 erreur Mypy).

#### Réserves à traiter impérativement lors des phases suivantes :
1. **En Phase 2 :** Ajouter l'anti-rejeu du code TOTP par pas de temps (time-step RFC 6238) au niveau de l'utilisateur pour interdire la validation d'un même code sur deux sessions simultanées.
2. **En Phase 2 :** Chiffrer la colonne `two_factor_secret` au repos (actuellement en clair en base).
3. **En Phase 4 / Déploiement :** Valider l'adresse IP cliente derrière les reverse proxies de confiance (`trusted proxies`) et purger les clés vides dans `InMemoryRateLimiter`.
