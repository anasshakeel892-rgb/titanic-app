from http.server import BaseHTTPRequestHandler
import json
import os

import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "titanic_model.pkl")
_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def engineer_features(passenger):
    """Mirrors the exact feature engineering used at training time.
    Must stay in lockstep with model/train_model.py or predictions
    will silently be wrong -- this is the #1 cause of a model that
    looks fine in the notebook but misbehaves once deployed."""

    name_title_map = {
        "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs",
        "Lady": "Rare", "Countess": "Rare", "Capt": "Rare", "Col": "Rare",
        "Don": "Rare", "Dr": "Rare", "Major": "Rare", "Rev": "Rare",
        "Sir": "Rare", "Jonkheer": "Rare", "Dona": "Rare",
    }

    title = passenger.get("title", "Mr")
    title = name_title_map.get(title, title)
    if title not in ["Mr", "Mrs", "Miss", "Master", "Rare"]:
        title = "Rare"

    sibsp = int(passenger.get("sibsp", 0))
    parch = int(passenger.get("parch", 0))
    family_size = sibsp + parch + 1
    is_alone = 1 if family_size == 1 else 0

    deck = passenger.get("deck") or "U"
    deck = deck[0].upper() if deck else "U"

    row = {
        "Pclass": int(passenger["pclass"]),
        "Sex": passenger["sex"],
        "Age": float(passenger["age"]),
        "Fare": float(passenger["fare"]),
        "Embarked": passenger.get("embarked", "S"),
        "Title": title,
        "FamilySize": family_size,
        "IsAlone": is_alone,
        "Deck": deck,
    }
    return pd.DataFrame([row])


def predict_passenger(passenger):
    model = get_model()
    X = engineer_features(passenger)
    proba = model.predict_proba(X)[0]
    survived_prob = float(proba[1])
    prediction = int(survived_prob >= 0.5)
    return {
        "prediction": prediction,
        "survived": bool(prediction),
        "survival_probability": round(survived_prob, 4),
        "death_probability": round(1 - survived_prob, 4),
    }


class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            passenger = json.loads(body or b"{}")

            required = ["pclass", "sex", "age", "fare"]
            missing = [f for f in required if f not in passenger]
            if missing:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": f"Missing required field(s): {', '.join(missing)}"
                }).encode())
                return

            result = predict_passenger(passenger)
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode())

        except Exception as exc:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(exc)}).encode())

    def do_GET(self):
        self._set_headers(200)
        self.wfile.write(json.dumps({
            "status": "ok",
            "message": "POST passenger details to this endpoint to get a prediction."
        }).encode())
