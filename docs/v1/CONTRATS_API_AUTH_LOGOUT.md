# Contrat API — Déconnexion

## Endpoint

`POST /auth/logout`

## Corps

```json
{ "refresh_token": "<jwt refresh>" }
```

## Comportement

1. Décode le jeton refresh (type `refresh`, présence de `jti`).
2. Insère le `jti` dans `revoked_refresh_tokens` (idempotent).
3. Répond `204 No Content`.

## Erreurs

| Cas | Code |
|---|---|
| Jeton invalide, expiré, ou non-refresh | `401` |

## Non-objectifs (compatibilité architecture)

- Aucune blacklist des jetons **access** : ils expirent naturellement.
- Pas de session serveur cookie : la session frontend reste dans `sessionStorage`.

## Frontend

`logout()` appelle cet endpoint puis `clearSession()`, même en cas d’échec réseau.
