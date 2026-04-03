Commande pour initialiser un projet vide d'un repo GIT déjà existant

```bash
uv init . --bare
```

Modifier la version de Python utilisée par défaut avec

```bash
uv python pin 3.12
```

Télécharger le fichier brut des gitignore

```bash
wget https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore
```

Démarrer une base de données pour assurer le tiers 3

```bash
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=gameboard postgres:latest
```

Installer les dépendances

```bash
uv add psycopg2-binary
```

## gRPC

Installer les modules gRPC

```bash
uv add grpcio grpcio-tools
```

Générer le code python à partir du fichier `gameboard.proto`

```bash
uv run python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. gameboard.proto
```