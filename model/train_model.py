import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

df = pd.read_csv("titanic_train.csv")
print("Raw shape:", df.shape)
print("Survived value counts:\n", df["Survived"].value_counts())

def engineer_features(df):
    df = df.copy()
    df["Title"] = df["Name"].str.extract(r",\s*([^\.]*)\.")
    title_map = {
        "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs",
        "Lady": "Rare", "Countess": "Rare", "Capt": "Rare", "Col": "Rare",
        "Don": "Rare", "Dr": "Rare", "Major": "Rare", "Rev": "Rare",
        "Sir": "Rare", "Jonkheer": "Rare", "Dona": "Rare"
    }
    df["Title"] = df["Title"].replace(title_map)
    df.loc[~df["Title"].isin(["Mr", "Mrs", "Miss", "Master", "Rare"]), "Title"] = "Rare"
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df["Deck"] = df["Cabin"].astype(str).str[0]
    df["Deck"] = df["Deck"].replace("nan", "U")
    return df

df = engineer_features(df)

feature_cols = ["Pclass", "Sex", "Age", "Fare", "Embarked", "Title", "FamilySize", "IsAlone", "Deck"]
X = df[feature_cols]
y = df["Survived"]

# Sanity check: does the raw data itself show the expected patterns?
print("\n--- Sanity check on raw data ---")
print("Survival rate by Sex:\n", df.groupby("Sex")["Survived"].mean())
print("\nSurvival rate by Pclass:\n", df.groupby("Pclass")["Survived"].mean())

numeric_features = ["Age", "Fare", "FamilySize"]
categorical_features = ["Pclass", "Sex", "Embarked", "Title", "IsAlone", "Deck"]

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])
preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(random_state=42))
])

param_grid = {
    "classifier__n_estimators": [200, 400],
    "classifier__max_depth": [4, 6, 8, None],
    "classifier__min_samples_leaf": [1, 2, 4]
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipeline, param_grid, cv=cv, scoring="accuracy", n_jobs=-1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_
print("\nBest params:", grid.best_params_)
print("Best CV accuracy:", grid.best_score_)

val_preds = best_model.predict(X_val)
print("\n--- Validation metrics ---")
print("Accuracy :", accuracy_score(y_val, val_preds))
print("Precision:", precision_score(y_val, val_preds))
print("Recall   :", recall_score(y_val, val_preds))
print("F1       :", f1_score(y_val, val_preds))

# Behavioral sense-checks: a few hand-built passengers that SHOULD be
# clearly high or clearly low survival probability, to confirm the model
# learned the right direction (not inverted, not random).
sense_checks = pd.DataFrame([
    # 1st class woman, young, high fare -> expect HIGH survival prob
    {"Pclass": 1, "Sex": "female", "Age": 24, "Fare": 100, "Embarked": "C",
     "Title": "Miss", "FamilySize": 1, "IsAlone": 1, "Deck": "B"},
    # 3rd class man, adult, low fare -> expect LOW survival prob
    {"Pclass": 3, "Sex": "male", "Age": 30, "Fare": 7, "Embarked": "S",
     "Title": "Mr", "FamilySize": 1, "IsAlone": 1, "Deck": "U"},
    # young boy, 3rd class -> "Master" title, women/children first, expect moderate-high
    {"Pclass": 3, "Sex": "male", "Age": 4, "Fare": 16, "Embarked": "S",
     "Title": "Master", "FamilySize": 3, "IsAlone": 0, "Deck": "U"},
])
probs = best_model.predict_proba(sense_checks)[:, 1]
print("\n--- Sense checks (should be HIGH, LOW, MODERATE-HIGH) ---")
for i, p in enumerate(probs):
    print(f"Case {i+1}: survival probability = {p:.3f}")

joblib.dump(best_model, "titanic_model.pkl")
print("\nSaved titanic_model.pkl")
