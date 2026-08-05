# TP GitHub Actions — de zéro à une pipeline complète

Chaque TP a : un objectif, ce que tu dois produire, des indices, et un
critère de réussite. Le fichier de correction correspondant est dans
`solutions/`, à consulter seulement après avoir essayé.

Tous les workflows vont dans `.github/workflows/`.

---

## TP 0 — Premier workflow (échauffement)

**Objectif** : comprendre la structure minimale d'un workflow et le voir
s'exécuter dans l'onglet "Actions" de GitHub.

**À faire** : crée `.github/workflows/hello.yml` qui se déclenche sur chaque
`push`, tourne sur `ubuntu-latest`, et affiche un message dans les logs
(`echo "Hello depuis Actions"`).

**Indices** :
- Un workflow a toujours `name`, `on`, `jobs`
- Un job a un `runs-on` et une liste de `steps`
- Une step simple utilise `run:` pour exécuter une commande shell

**Critère de réussite** : après un `git push`, l'onglet Actions de ton repo
GitHub montre une run verte avec ton message dans les logs.

---

## TP 1 — Pipeline CI : lint + tests

**Objectif** : la vraie première pipeline utile. À chaque push et pull
request, on installe les dépendances, on lint le code et on lance les tests.

**À faire** : crée `.github/workflows/ci.yml` qui :
1. Se déclenche sur `push` et `pull_request` (branches `main` uniquement pour push)
2. Checkout le code (`actions/checkout`)
3. Installe Python (`actions/setup-python`) — utilise une **matrice** pour
   tester sur Python 3.11 et 3.12
4. Installe les dépendances (`pip install -r requirements.txt`)
5. Lance `flake8 app tests`
6. Lance `pytest -q`

**Indices** :
- `strategy.matrix.python-version: ["3.11", "3.12"]`
- Dans `setup-python`, `python-version: ${{ matrix.python-version }}`
- Si flake8 remonte des erreurs sur du code que tu n'as pas écrit, corrige-les
  (ou ajuste `.flake8`, mais essaie d'abord de comprendre l'erreur)

**Critère de réussite** : casse volontairement un test (modifie une assertion),
push, et vérifie que la pipeline échoue en rouge avec un message clair dans
les logs. Puis répare et vérifie qu'elle repasse au vert.

---

## TP 2 — Cache & artifacts

**Objectif** : accélérer la pipeline et conserver des preuves d'exécution
(rapport de couverture de tests).

**À faire** : modifie `ci.yml` pour :
1. Mettre en cache les dépendances pip (`actions/cache`, clé basée sur le hash
   de `requirements.txt`)
2. Générer un rapport de couverture avec `pytest --cov=app --cov-report=html`
3. Uploader ce rapport comme artifact (`actions/upload-artifact`), consultable
   depuis l'onglet Actions après la run

**Indices** :
- `actions/setup-python` a un paramètre `cache: pip` qui peut suffire — teste
  la différence de temps d'exécution avec/sans
- `hashFiles('requirements.txt')` dans la clé de cache

**Critère de réussite** : télécharge le rapport HTML depuis une run terminée
et ouvre-le en local pour voir la couverture de code.

---

## TP 3 — Build & push d'une image Docker

**Objectif** : construire l'image Docker de l'API et la publier sur le
GitHub Container Registry (GHCR) — un vrai réflexe DevOps.

**À faire** : crée `.github/workflows/docker.yml` qui :
1. Se déclenche uniquement sur push sur `main` (pas sur les PR — on ne publie
   pas une image pour du code non mergé)
2. Se connecte à GHCR avec `docker/login-action` (utilise le `GITHUB_TOKEN`
   automatique, pas de secret à créer)
3. Build et push l'image avec `docker/build-push-action`, tag
   `ghcr.io/<ton-user>/bankflow-api:latest` et aussi `:${{ github.sha }}`

**Indices** :
- Permissions : le job a besoin de `permissions: packages: write`
- `docker/build-push-action` prend `context: .`, `push: true`, `tags: ...`

**Critère de réussite** : l'image apparaît dans l'onglet "Packages" de ton
profil GitHub après une run réussie.

---

## TP 4 — Environnements et déploiement avec validation manuelle

**Objectif** : simuler un vrai déploiement contrôlé (staging → production),
comme tu le verras probablement en entreprise.

**À faire** :
1. Crée deux environnements dans les Settings du repo : `staging` et
   `production`. Ajoute une règle de "required reviewer" sur `production`.
2. Modifie/crée un workflow avec deux jobs séquentiels : `deploy-staging`
   (automatique après le build) puis `deploy-production` (nécessite
   l'approbation manuelle via l'environnement `production`)
3. Le "déploiement" peut être un simple `echo "Déploiement vers staging/prod"`
   — l'objectif ici est le mécanisme d'approbation, pas un vrai déploiement.

**Indices** :
- `environment: staging` / `environment: production` au niveau du job
- `needs: deploy-staging` pour chaîner les jobs

**Critère de réussite** : la run se met en pause avant `deploy-production` et
attend que tu cliques sur "Approve" dans l'interface GitHub.

---

## TP 5 — Sécurité : analyse de code et dépendances

**Objectif** : ajouter les réflexes sécurité attendus en environnement
bancaire — scan de vulnérabilités et analyse statique.

**À faire** :
1. Active **Dependabot** (fichier `.github/dependabot.yml`) pour surveiller
   les mises à jour de `requirements.txt` chaque semaine
2. Ajoute un workflow `codeql.yml` utilisant `github/codeql-action` pour
   scanner le code Python à chaque push sur `main` et chaque PR
3. Bonus : ajoute un scan de vulnérabilités sur l'image Docker avec `trivy`
   (action `aquasecurity/trivy-action`) dans le workflow du TP 3

**Indices** :
- GitHub propose un template CodeQL prêt à l'emploi dans l'onglet Security
  → Code scanning — utilise-le comme base puis comprends-le
- `dependabot.yml` a un `package-ecosystem: "pip"` et un `schedule.interval`

**Critère de réussite** : l'onglet "Security" de ton repo montre des résultats
de scan CodeQL (même si c'est "0 alertes trouvées").

---

## TP 6 — Aller plus loin : workflow réutilisable

**Objectif** : factoriser. Si tu avais 5 microservices avec la même logique
de CI, tu ne veux pas copier-coller le YAML 5 fois.

**À faire** : extrais la partie "lint + tests" du TP 1 dans un workflow
réutilisable (`workflow_call`), puis appelle-le depuis `ci.yml`.

**Indices** :
- Un workflow réutilisable a `on: workflow_call` au lieu de `on: push`
- On l'appelle avec `uses: ./.github/workflows/reusable-ci.yml`

**Critère de réussite** : `ci.yml` fait moins de 10 lignes et délègue tout le
travail au workflow réutilisable.

---

## Pour aller encore plus loin (optionnel)

- Ajoute un `pre-commit` hook qui lance flake8/black en local avant chaque commit
- Ajoute la création automatique d'une release GitHub avec changelog quand tu
  pousses un tag `v*`
- Explore `act` (https://github.com/nektos/act) pour exécuter tes workflows
  GitHub Actions en local sans pusher à chaque essai
