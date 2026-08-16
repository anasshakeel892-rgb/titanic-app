# Titanic Survival Predictor — Full-Stack App

A real full-stack app: a Next.js frontend form that calls a Python backend
(`api/predict.py`) which loads **your own trained model**
(`api/titanic_model.pkl` — the exact file you exported from your Colab
notebook) and returns real predictions. The model runs server-side, same
as it did in Colab — nothing client-side is approximating it.

## Verified before delivery

Your uploaded `titanic_model.pkl` was loaded and sense-checked against
known cases before being wired into this app:

| Passenger | Survival probability |
|---|---|
| 1st class woman, age 24 | 94.3% |
| 3rd class man, age 30 | 9.9% |
| 3rd class boy, age 4 | 63.2% |

These are the expected patterns (women and children first, 1st class
favored), confirming your model learned correctly. The full round trip
(HTTP request → `api/predict.py` → your model → response) was also tested
directly before this zip was packaged.

## Project structure

```
titanic-app/
  app/                        Next.js frontend (the form + result UI)
  api/
    predict.py                Python serverless function — loads the model, predicts
    titanic_model.pkl         YOUR trained model (RandomForest, from your Colab)
    requirements.txt          Python deps, pinned to match your Colab's versions
  model/
    train_model.py            Reference script matching your notebook's feature engineering
    your_trained_model.pkl    A backup copy of your uploaded model
  vercel.json                 Tells Vercel to run api/predict.py as a Python function
```

## How it works

1. You fill out the form (class, sex, age, fare, family aboard, port).
2. The frontend sends that as JSON to `POST /api/predict`.
3. `api/predict.py` engineers the same features your notebook used
   (title, family size, deck, etc.), feeds them into YOUR pickled model,
   and returns `{ survived, survival_probability, ... }`.
4. The frontend displays the result.

## Deploy on Vercel

1. Push this whole folder to a new GitHub repo.
2. On vercel.com → New Project → import that repo.
3. Vercel auto-detects the Next.js frontend AND the Python function in
   `api/predict.py` (thanks to `vercel.json` + `api/requirements.txt`) —
   no extra configuration needed.
4. Deploy. Your form will call your real model at `https://your-app.vercel.app/api/predict`.

## Retraining later

If you retrain in Colab again:

1. Re-run `joblib.dump(best_model, "titanic_model.pkl")` and download it.
2. Replace `api/titanic_model.pkl` with the new file (same filename).
3. Re-check your Colab's `sklearn` / `pandas` / `joblib` versions and
   update `api/requirements.txt` if they changed.
4. Push to GitHub — Vercel redeploys automatically.

## If predictions ever look wrong again

- **Feature mismatch at predict time** — the columns fed into `.predict()`
  must exactly match what the model was fit on. `api/predict.py` mirrors
  your notebook's `engineer_features()` function; if you change feature
  engineering in Colab, update `api/predict.py` to match.
- **Version mismatch** — a model pickled with one scikit-learn version can
  misbehave on another. Keep `api/requirements.txt` matched to your
  Colab's versions.
- **Threshold confusion** — `.predict()` uses a 0.5 cutoff; borderline
  cases near 0.5 aren't "wrong," just close calls.
