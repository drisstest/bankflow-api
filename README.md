# BankFlow API — Projet d'entraînement GitHub Actions

Mini API REST de gestion de comptes bancaires (Flask), volontairement simple,
pour te concentrer sur la mise en place d'une pipeline CI/CD avec **GitHub
Actions** — dans un thème proche de ce que tu retrouveras en alternance chez SG.

## Le projet

- `app/models.py` — logique métier (comptes, dépôts, retraits, virements, règles)
- `app/main.py` — API Flask (endpoints REST)
- `tests/` — tests unitaires et d'intégration (pytest), déjà écrits et qui passent
- `Dockerfile` — pour containeriser l'API
- `requirements.txt` — dépendances (flask, pytest, flake8, black...)

## Lancer en local

```bash
pip install -r requirements.txt
python -m pytest -q          # lancer les tests
python -m flask --app app.main run  # lancer l'API sur http://127.0.0.1:5000
```

Endpoints principaux : `GET /health`, `POST /accounts`, `GET /accounts/<id>`,
`POST /accounts/<id>/deposit`, `POST /accounts/<id>/withdraw`, `POST /transfer`.

## Comment travailler

1. Crée un repo GitHub vide, pousse ce projet dedans.
2. Ouvre `TP.md` et fais les TP **dans l'ordre**, un commit/une pull request
   par TP si possible (ça t'entraîne aussi au workflow git).
3. Le dossier `solutions/` contient une correction pour chaque TP : n'y jette
   un oeil qu'**après** avoir essayé — sinon tu n'apprends rien, tu recopies.
4. Chaque TP est indépendant mais s'appuie sur le précédent, comme une vraie
   pipeline qui grossit avec le temps.

Bon courage, et n'hésite pas à casser des choses volontairement pour voir
comment les logs d'Actions réagissent : c'est le meilleur moyen d'apprendre.
