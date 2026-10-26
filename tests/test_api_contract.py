from fastapi.testclient import TestClient
from churn.app import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_rejects_invalid_input():
    with TestClient(app) as client:
        response = client.post("/predict", json={})

    assert response.status_code == 422


def test_predict_returns_probability_and_model_version():
    kund = {
        "alder": 35,
        "manadskostnad": 399.0,
        "manader_som_kund": 24,
        "abonnemang": "Bas",
        "region": "Stockholm",
        "data_gb_per_manad": 15.0,
        "supportarenden_12m": 1,
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=kund)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["sannolikhet"], float)
        assert 0.0 <= data["sannolikhet"] <= 1.0
        assert isinstance(data["model_version"], str)
        assert data["model_version"]
