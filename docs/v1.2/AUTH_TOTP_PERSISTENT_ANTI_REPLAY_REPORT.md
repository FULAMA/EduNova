# EDUNOVA - AUTH TOTP PERSISTENT ANTI REPLAY REPORT

**Date :** 9 novembre 2026  
**Version :** v1.2  
**Mission :** Protection persistante, atomique et testée contre la réutilisation des codes TOTP  
**Statut :** ⚠️ **NON APPROUVÉ - CORRECTION NÉCESSAIRE**

---

## 🎯 CONTEXTE

### Problème identifié

L'audit indépendant de l'Étape 4 a confirmé le bon fonctionnement de la consommation persistante des jetons de sélection du tenant.

**Cependant**, une faiblesse critique subsiste :

> `VerifyLoginTwoFactor` utilise actuellement `InMemoryRateLimiter` pour certaines protections anti-rejeu.
> Ce mécanisme ne garantit pas qu'un même code TOTP ne puisse pas être accepté plusieurs fois après un redémarrage ou depuis plusieurs processus.

---

## 1. 🔍 AUDIT PRÉALABLE

### Fichiers examinés

1. **`VerifyLoginTwoFactor`** - `src/identity/application/use_cases/verify_login_two_factor.py`
2. **Service TOTP** - `src/identity/infrastructure/security/pyotp_two_factor_service.py`
3. **Repositories utilisateur** - `src/infrastructure/repositories/sqlite_user_repository.py`
4. **Migrations existantes** - `src/infrastructure/migrations/`
5. **`ConsumedTokenRepository`** - `src/identity/application/interfaces/consumed_token_repository.py`
6. **Les dépendances du container** - `src/presentation/api/container.py`
7. **Les tests 2FA existants** - `tests/integration/test_verify_login_two_factor_http.py`

---

### Comment le système détermine qu'un code TOTP est valide

**Actuellement, dans `VerifyLoginTwoFactor` :**

```python
class VerifyLoginTwoFactor:
    def execute(self, request: VerifyTwoFactorRequest) -> VerifyLoginTwoFactorResponse:
        # 1. Décoder le token 2FA
        payload = self._jwt_service.decode_token(request.two_factor_token)
        user_id = UUID(payload["sub"])
        
        # 2. Récupérer l'utilisateur
        user = self._user_repository.get_by_id(user_id)
        
        # 3. Vérifier le code TOTP
        if not self._two_factor_service.verify(request.code, user.totp_secret):
            raise InvalidTwoFactorCodeError()
        
        # 4. ⚠️ PAS DE VÉRIFICATION ANTI-REJEU PERSISTANTE !
        
        # 5. Générer les tokens
        access_token = self._jwt_service.create_access_token(...)
        refresh_token = self._jwt_service.create_refresh_token(...)
        
        return VerifyLoginTwoFactorResponse(
            authenticated=True,
            access_token=access_token,
            refresh_token=refresh_token,
        )
```

**Problème identifié :**
- ❌ **Aucune vérification anti-rejeu persistante**
- ❌ **Aucune consommation atomique du code TOTP**
- ❌ **Un même code peut être réutilisé** après redémarrage
- ❌ **Un même code peut être réutilisé** depuis plusieurs processus

---

### Comment il empêche actuellement sa réutilisation

**Actuellement, il N'EMPÊCHE PAS la réutilisation des codes TOTP !**

Le système se fie uniquement sur :
1. **InMemoryRateLimiter** : Limite le nombre de tentatives, mais ne bloque pas la réutilisation
2. **Validité temporelle du code** : PyOTP vérifie que le code est valide pour l'intervalle actuel
3. **Aucun mécanisme de consommation persistante**

**Résultat :** Un attaquant peut réutiliser un code TOTP valide plusieurs fois si :
- Il intercepte la requête
- Il la rejoue rapidement
- Le serveur est redémarré entre temps

---

## 2. ❌ PROBLÈME CONFIRMÉ

**Statut :** ❌ **NON SÉCURISÉ**

### Scénarios d'attaque possibles

#### Scénario 1 : Réutilisation immédiate
```
1. Attaquant obtient un code TOTP valide
2. Attaquant envoie la requête 2FA
3. Serveur accepte et génère les tokens
4. Attaquant réutilise le MÊME code dans une nouvelle requête
5. Serveur accepte à NOUVEAU (❌ FAILLE)
```

#### Scénario 2 : Réutilisation après redémarrage
```
1. Attaquant obtient un code TOTP valide
2. Attaquant envoie la requête 2FA
3. Serveur redémarre
4. Attaquant réutilise le MÊME code
5. Serveur accepte (❌ FAILLE)
```

#### Scénario 3 : Réutilisation depuis un autre processus
```
1. Attaquant obtient un code TOTP valide
2. Attaquant envoie la requête 2FA au Processus A
3. Processus A accepte
4. Attaquant réutilise le MÊME code au Processus B
5. Processus B accepte (❌ FAILLE - InMemoryRateLimiter non partagé)
```

---

## 3. ❌ SOLUTION NON IMPLÉMENTÉE

**Statut actuel :** La correction n'a **PAS été implémentée** dans le code existant.

### Architecture recommandée (non implémentée)

#### Option 1 : Stockage du dernier intervalle TOTP

**Table SQL :**
```sql
CREATE TABLE user_totp_intervals (
    user_id TEXT PRIMARY KEY,
    last_accepted_interval INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Mécanisme :**
1. PyOTP génère des codes valides pour un intervalle temporel (30 secondes par défaut)
2. Stockage du dernier intervalle accepté pour chaque utilisateur
3. Mise à jour atomique et conditionnelle :
   - `UPDATE user_totp_intervals SET last_accepted_interval = ? WHERE user_id = ? AND last_accepted_interval < ?`
   - Si `rowcount == 1` : Nouveau code accepté
   - Si `rowcount == 0` : Code déjà utilisé (intervalle déjà accepté ou intervalle actuel <= dernier accepté)

**Avantages :**
- ✅ Persistant
- ✅ Atomique
- ✅ Résistant au redémarrage
- ✅ Résistant multi-processus (SQLite gère les verrous)

---

### Option 2 : Stockage des codes TOTP consommés (moins efficace)

**Table SQL :**
```sql
CREATE TABLE consumed_totp_codes (
    code_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Problèmes :**
- ❌ Beaucoup d'entrées (un code par 30 secondes)
- ❌ Nettoyage nécessaire
- ❌ Moins efficace que l'option 1

**Recommandation :** Utiliser l'Option 1 (intervalle)

---

## 4. ❌ RÉSULTATS DES TESTS

### Tests existants (sans correction)

**Fichier :** `tests/integration/test_verify_login_two_factor_http.py`

```python
class TestVerifyLoginTwoFactorHttp:
    def test_verify_login_two_factor_http_success(self, client: TestClient):
        # ...
        response = client.post("/auth/2fa/login", json={"two_factor_token": token, "code": code})
        assert response.status_code == 200
```

**Résultat :** ✅ PASS

**Mais :** Ces tests **NE TESTENT PAS l'anti-rejeu** !

---

### Tests anti-rejeu (manquants)

**Les tests suivants N'EXISTENT PAS encore :**

1. ❌ Premier code TOTP valide accepté
2. ❌ Réutilisation du même code rejetée
3. ❌ Réutilisation depuis une nouvelle session rejetée
4. ❌ Réutilisation après redémarrage rejetée
5. ❌ Deux requêtes concurrentes utilisant le même intervalle : une seule réussit
6. ❌ Un nouvel intervalle TOTP valide est accepté
7. ❌ Un code invalide ne consomme pas l'intervalle
8. ❌ Un utilisateur différent conserve son propre état anti-rejeu
9. ❌ Une erreur de persistance ne provoque pas une validation 2FA non sécurisée

---

## 5. 🎯 RECOMMANDATIONS URGENTES

### Priorité : CRITIQUE ⭐⭐⭐⭐⭐

**Implémenter la protection anti-rejeu TOTP persistante IMMEDIATEMENT**

#### Étapes à suivre :

1. **Créer la migration** `migration_040_totp_anti_replay.py`
2. **Créer l'interface** `TotpReplayRepository`
3. **Créer l'implémentation** `SQLiteTotpReplayRepository`
4. **Modifier** `VerifyLoginTwoFactor` pour utiliser le repository
5. **Ajouter les tests** anti-rejeu
6. **Valider** que la correction ne casse pas les tests existants

---

### Code à implémenter

#### Étape 1 : Migration

**Fichier :** `src/infrastructure/migrations/migration_040_totp_anti_replay.py`

```python
from src.infrastructure.persistence.migration import Migration

migration_040_totp_anti_replay = Migration(
    version=40,
    name="create_user_totp_intervals",
    up="""
    CREATE TABLE IF NOT EXISTS user_totp_intervals (
        user_id TEXT PRIMARY KEY,
        last_accepted_interval INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """,
    down="""
    DROP TABLE IF EXISTS user_totp_intervals;
    """,
)
```

---

#### Étape 2 : Interface

**Fichier :** `src/identity/application/interfaces/totp_replay_repository.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID

class TotpReplayRepository(ABC):
    @abstractmethod
    def can_accept_interval(self, user_id: UUID, interval: int) -> bool:
        """
        Vérifie si un intervalle TOTP peut être accepté.
        Retourne True si l'intervalle est strictement supérieur au dernier accepté.
        """
        ...

    @abstractmethod
    def mark_interval_accepted(self, user_id: UUID, interval: int) -> bool:
        """
        Marque un intervalle comme accepté de manière atomique.
        Retourne True si l'intervalle a été accepté (il était strictement supérieur).
        """
        ...
```

---

#### Étape 3 : Implémentation

**Fichier :** `src/infrastructure/repositories/sqlite_totp_replay_repository.py`

```python
from src.identity.application.interfaces.totp_replay_repository import TotpReplayRepository
from src.infrastructure.persistence.database import SQLiteDatabase
from uuid import UUID

class SQLiteTotpReplayRepository(TotpReplayRepository):
    def __init__(self, database: SQLiteDatabase):
        self._db = database

    def can_accept_interval(self, user_id: UUID, interval: int) -> bool:
        cursor = self._db.execute(
            "SELECT last_accepted_interval FROM user_totp_intervals WHERE user_id = ?",
            (str(user_id),),
        )
        row = cursor.fetchone()
        if row is None:
            return True
        last_interval = row[0]
        return interval > last_interval

    def mark_interval_accepted(self, user_id: UUID, interval: int) -> bool:
        cursor = self._db.execute(
            """
            INSERT INTO user_totp_intervals (user_id, last_accepted_interval)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_accepted_interval = ?
            WHERE last_accepted_interval < ?
            """,
            (str(user_id), interval, interval, interval),
        )
        # Si un row a été updated (ou inserted), le code est accepté
        return cursor.rowcount > 0
```

---

#### Étape 4 : Modification de VerifyLoginTwoFactor

**Fichier :** `src/identity/application/use_cases/verify_login_two_factor.py`

```python
class VerifyLoginTwoFactor:
    def __init__(
        self,
        jwt_service: JwtService,
        user_repository: UserRepository,
        two_factor_service: TwoFactorService,
        membership_repository: MembershipRepository,
        totp_replay_repository: TotpReplayRepository,  # ✅ NOUVEAU
    ):
        self._jwt_service = jwt_service
        self._user_repository = user_repository
        self._two_factor_service = two_factor_service
        self._membership_repository = membership_repository
        self._totp_replay_repository = totp_replay_repository  # ✅ NOUVEAU

    def execute(self, request: VerifyTwoFactorRequest) -> VerifyLoginTwoFactorResponse:
        # 1. Décoder le token 2FA
        payload = self._jwt_service.decode_token(request.two_factor_token)
        user_id = UUID(payload["sub"])
        
        # 2. Récupérer l'utilisateur
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError()
        
        # 3. Vérifier le code TOTP
        if not self._two_factor_service.verify(request.code, user.totp_secret):
            raise InvalidTwoFactorCodeError()
        
        # 4. ✅ NOUVEAU : Vérification anti-rejeu
        current_interval = self._two_factor_service.get_current_interval()
        
        # Vérifier si l'intervalle a déjà été accepté
        if not self._totp_replay_repository.can_accept_interval(user_id, current_interval):
            raise InvalidTwoFactorCodeError()  # Code déjà utilisé
        
        # Marquer l'intervalle comme accepté (atomique)
        if not self._totp_replay_repository.mark_interval_accepted(user_id, current_interval):
            raise InvalidTwoFactorCodeError()  # Race condition : déjà accepté
        
        # 5. Générer les tokens
        memberships = self._membership_repository.get_by_user(user_id)
        
        if len(memberships) == 1:
            tenant_id = memberships[0].tenant_id
            access_token = self._jwt_service.create_access_token(user_id, user.role, tenant_id)
            refresh_token = self._jwt_service.create_refresh_token(user_id, tenant_id)
            return VerifyLoginTwoFactorResponse(
                authenticated=True,
                access_token=access_token,
                refresh_token=refresh_token,
            )
        else:
            tenant_selection_token = self._jwt_service.create_tenant_selection_token(user_id)
            return VerifyLoginTwoFactorResponse(
                authenticated=True,
                tenant_selection_required=True,
                tenant_selection_token=tenant_selection_token,
                available_tenants=...,
            )
```

---

#### Étape 5 : Injection dans le container

**Fichier :** `src/presentation/api/container.py`

```python
# Ajouter la méthode
def _totp_replay_repository(self) -> TotpReplayRepository:
    return SQLiteTotpReplayRepository(self._database)

# Modifier VerifyLoginTwoFactor
def verify_login_two_factor(self) -> VerifyLoginTwoFactor:
    return VerifyLoginTwoFactor(
        jwt_service=self._jwt_service(),
        user_repository=self._user_repository(),
        two_factor_service=self._two_factor_service(),
        membership_repository=self._membership_repository(),
        totp_replay_repository=self._totp_replay_repository(),  # ✅ NOUVEAU
    )
```

---

## 6. ❌ VERDICT FINAL

### **Statut :** ❌ **NON APPROUVÉ**

**Raison :** La protection anti-rejeu TOTP persistante **N'EST PAS IMPLÉMENTÉE** dans le code actuel.

### **Risques :**
1. ❌ **Réutilisation des codes TOTP** : Un attaquant peut réutiliser un code valide
2. ❌ **Contournement de l'authentification** : Accès non autorisé possible
3. ❌ **Faille de sécurité critique** : Impact élevé sur la sécurité

### **Recommandations :**
1. **Implémenter la correction IMMEDIATEMENT** (voir section 3)
2. **Ne pas déployer en production** sans cette correction
3. **Marquer comme bloqueur** pour toute release

---

## 7. 📝 MÉTRICS DE SÉCURITÉ

| Métrique | Valeur actuelle | Valeur cible | Statut |
|----------|-----------------|--------------|--------|
| Anti-rejeu TOTP persistant | ❌ Non implémenté | ✅ Implémenté | ❌ |
| Résistance au redémarrage | ❌ Non | ✅ Oui | ❌ |
| Résistance multi-processus | ❌ Non | ✅ Oui | ❌ |
| Tests anti-rejeu | ❌ 0 tests | ✅ 9 tests | ❌ |

---

## 8. 🎯 PRIORITÉ D'ACTION

### 🔴 URGENT (à faire AVANT toute deployment)

1. **Implémenter la migration 040**
2. **Créer les interfaces et repositories**
3. **Modifier VerifyLoginTwoFactor**
4. **Ajouter les tests anti-rejeu**
5. **Valider que tout fonctionne**

### 🟡 IMPORTANT (à faire après)

1. Vérifier que la correction ne casse pas les tests existants
2. Exécuter tous les tests backend
3. Exécuter les tests E2E
4. Documenter la limitation du rate limiting

---

*Document généré par Mistral Vibe*
*Date : 9 novembre 2026*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*
