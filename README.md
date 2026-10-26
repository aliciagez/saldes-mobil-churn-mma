# Churnmodellen – Saldes Mobil-Churn-MMA

## Om vårt grupparbete

I den här laborationen bygger vi vidare på en övning från läraren Saldes-mobil churn. Vårt uppdrag är att bygga en CI/CD-pipeline som automatiskt testar, validerar, versionerar och paketerar en ML-modell.

Syftet är att vi ska lära oss hur ett MLOps-team arbetar i praktiken.

En viktig grundregel är att alla ändringar ska gå via Pull Requests (PR), där vi granskar varandras arbete innan ändringarna mergas till `main`.

Vi har delat upp arbetet mellan gruppmedlemmarna. Mer information om vårt arbetssätt finns i dokumentet **Way of Working** i repositoryt.

Vi använder även Kanban i Tabula för att fördela uppgifter och följa varandras framsteg.

## Så kör man det lokalt

## Installera beroenden

Projektet använder uv och Python 3.11 i CI 

```bash
uv sync --frozen --extra dev
``` 

## Kör tester

```bash
uv run --extra dev pytest -v
```
## Träna och utvärdera modellen

```bash
uv run python -m churn.model
uv run python -m churn.evaluate
```
## Kör FastApi lokalt 

1. Ladda ner artefakten approved-modell-<sha> från Github actions
2. Packa upp filerna modell.joblib (modell )och matvarden.json (mätvärden)
3. Placera dem i approved-model/ i projektets rotmapp 

Starta sedan API:et med följande kommando 

uv run uvicorn churn.app:app --reload 
Dokumentationen hittar du här : http://127.0.0.1:8000/docs 

Endpoints 

GET/health : testar om API:et startar ska returnera "status:ok"
POST/predict : Modellen gör en beräkning  och returnerar sannolikhet samt model_version
{
  "sannolikhet": 0.78,
  "model_version": "a87a8d5..."
}

## Kör API-kontrakttester
```bash
uv run --extra dev pytest tests/test_api_contract.py -v
```











