from fastapi import FastAPI 
from pydantic import BaseModel 

import pandas as pd 
from churn.data import skapa_features, FEATURES 
from pathlib import Path 
import joblib 
MODELLFIL= Path("approved-model/modell.joblib")
modell=joblib.load(MODELLFIL)
import json
matvarden = json.loads(Path("approved-model/matvarden.json").read_text()) # 
modellversion= matvarden["commit"]

app = FastAPI()

@app.get("/health")
def health():
    return{"status":"ok"}

class Kund(BaseModel):
    alder:int 
    manadskostnad: float
    manader_som_kund: int
    abonnemang: str
    region:str
    data_gb_per_manad:float
    supportarenden_12m: int 

@app.post("/predict")
def predict(kund:Kund): 
  df =pd.DataFrame([kund.model_dump()])
  df = skapa_features(df)
  sannolikhet= modell.predict_proba(df[FEATURES])[0,1] ### LLM ASSISTANCE 
  return {"sannolikhet":float(sannolikhet),
          "model_version": modellversion}
# Enligt våra regler skulle den printa sannolikhet och model version därav ändringen


#fungerade inte först , kollade pyproject.toml under dependencies, fanns ej kör uv add fastapi

