# Contrats API manquants (constatés par le frontend)

Le backend n'a pas été modifié. Ces points bloquent ou limitent des écrans.

| Besoin | État constaté | Impact frontend |
|---|---|---|
| Déconnexion avec révocation du refresh token | Aucune route `logout` ou `revoke` dans `auth.py` | La déconnexion ne vide que la session locale |
| Création / modification d'un élève | `GET /students` seulement | Pas d'écran de création ni d'édition |
| Recherche d'élève pour les rôles financiers | `GET /students` réservé à ADMIN | DIRECTION, ACCOUNTANT et CASHIER ne peuvent pas choisir un élève : paiements impossibles |
| Liste globale des paiements et des reçus | Seulement `GET /billing/students/{id}/summary` | Consultation par élève uniquement |
| Rôles PROF et PARENT | Non confirmés dans les dépendances de rôles | Aucun portail enseignant ou parent |