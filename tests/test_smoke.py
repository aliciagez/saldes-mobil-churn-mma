import requests

BASE_URL = "http://localhost:8000/"

def test_health():
    respose=requests.get(f"{BASE_URL}/health", timeout=5)
    assert respose.status_code == 200
    assert respose.json()["status"] == "ok"

def test_predict():
    kund = {
          "alder": 35,
          "manadskostnad": 399.0,
          "manader_som_kund": 24,
          "abonnemang": "Bas",
          "region": "Stockholm",
           "data_gb_per_manad": 15.0,
           "supportarenden_12m": 1,
    }

    response = requests.post(
        f"{BASE_URL}/predict",
        json=kund,
        timeout=5,
    ) 
    assert response.status_code == 200

    data = response.json()

    assert 0 <= data["sannolikhet"] <= 1
    assert data["model_version"]