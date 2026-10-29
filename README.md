
# Churnmodellen – Saldes Mobil-Churn-MMA

## Om vårt grupparbete

I den här laborationen bygger vi vidare på en övning från läraren, Saldes Mobil-Churn. Vårt uppdrag är att bygga en CI/CD-pipeline som automatiskt testar, validerar, versionerar och paketerar en ML-modell.

Syftet är att vi ska lära oss hur ett MLOps-team arbetar i praktiken.

En viktig grundregel är att alla ändringar ska gå via Pull Requests (PR), där vi granskar varandras arbete innan ändringarna mergas till `main`.

Vi har delat upp arbetet mellan gruppmedlemmarna. Mer information om vårt arbetssätt finns i dokumentet **Way of Working** i repositoryt.

Vi använder även Kanban i Tabula för att fördela uppgifter och följa varandras framsteg.

## Så kör man det lokalt

### Installera beroenden

Projektet använder `uv` och Python 3.11 i CI.

```bash
uv sync --frozen --extra dev
```

### Kör tester

```bash
uv run --extra dev pytest -v
```

### Träna och utvärdera modellen

```bash
uv run python -m churn.model
uv run python -m churn.evaluate
```

### Kör FastAPI lokalt

1. Ladda ner artefakten `approved-modell-<sha>` från GitHub Actions.
2. Packa upp filerna `modell.joblib` (modell) och `matvarden.json` (mätvärden).
3. Placera dem i `approved-model/` i projektets rotmapp.

Starta sedan API:et med följande kommando:

```bash
uv run uvicorn churn.app:app --reload
```

Dokumentationen hittar du här: http://127.0.0.1:8000/docs

### Endpoints

`GET /health`: Testar om API:et har startat och ska returnera `"status": "ok"`.

`POST /predict`: Modellen gör en beräkning och returnerar sannolikhet samt `model_version`.

```json
{
  "sannolikhet": 0.78,
  "model_version": "a87a8d5..."
}
```

### Kör API-kontrakttester

```bash
uv run --extra dev pytest tests/test_api_contract.py -v
```

## Kör applikationen med Docker

I detta projekt använder vi Docker för att paketera FastAPI-applikationen, den godkända ML-modellen och dess beroenden i en container.

För att köra applikationen med Docker:

1. Se till att Docker Desktop är igång samt att mappen `approved-model/` innehåller modellfilerna `matvarden.json` och `modell.joblib`.

### Bygg Docker-imagen från projektets rotmapp

```bash
docker build -t churn-api .
```

### Starta containern

```bash
docker run --rm -p 8000:8000 churn-api
```

## Docker, smoke tests och GHCR i CI/CD

GitHub Actions testar och bygger Docker-imagen automatiskt som en del av vår CI/CD-pipeline.

### Smoke tests

När containern startas väntar workflowen tills endpointen `/health` svarar. Därefter körs:

```bash
uv run --extra dev pytest tests/test_smoke.py -v
```

Smoke tests är tester som kontrollerar att API:ets grundläggande funktioner fungerar efter att det har startats. Om ett test inte går igenom avbryts jobbet och containerloggar visas för felsökning.

### Publicering till GHCR

Vårt projekt använder GitHub Container Registry (GHCR) för att lagra Docker Images.

Workflowen loggar in på GHCR med hjälp av GitHubs inbyggda `GITHUB_TOKEN`.

När workflowen körs från `main` publiceras imagen med en tagg som representerar den aktuella commit-SHA:n.

Detta gör att vi kan identifiera vilken kodversion som finns i varje publicerad image.
