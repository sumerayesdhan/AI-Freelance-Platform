import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

import joblib


# ============================================================
# STEP 1: LOAD TRAINING DATA
# ============================================================

print("Loading training dataset...")

df = pd.read_csv(
    "data/recommendation_training.csv"
)

print("Dataset shape:", df.shape)


# ============================================================
# STEP 2: SELECT FEATURES
# ============================================================

feature_columns = [
    "cosine_similarity",
    "skill_match",
    "experience_score",
    "job_success",
    "total_jobs",
    "total_hours",
    "hourly_rate",
    "project_budget",
    "hourly_low",
    "hourly_high",
    "budget_compatibility",
    "country_match",
    "matching_skill_count",
    "required_skill_count"
]


X = df[feature_columns].copy()

y = df["label"]


# ============================================================
# STEP 3: HANDLE MISSING VALUES
# ============================================================

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(0)


print("\nFeatures used for training:")

for feature in feature_columns:
    print("-", feature)


# ============================================================
# STEP 4: CHECK TARGET DISTRIBUTION
# ============================================================

print("\nTarget distribution:")

print(
    y.value_counts()
)

print("\nTarget percentage:")

print(
    y.value_counts(normalize=True) * 100
)


# ============================================================
# STEP 5: TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# STEP 6: CREATE XGBOOST MODEL
# ============================================================

print("\nCreating XGBoost model...")

model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# STEP 7: TRAIN MODEL
# ============================================================

print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train
)


print("\nXGBoost training completed!")


# ============================================================
# STEP 8: PREDICTIONS
# ============================================================

y_pred = model.predict(
    X_test
)

y_probability = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# STEP 9: EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========================================")
print("XGBOOST MODEL EVALUATION")
print("========================================")

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print(
    f"ROC-AUC   : {roc_auc:.4f}"
)


# ============================================================
# STEP 10: CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Not Recommended",
            "Recommended"
        ],
        zero_division=0
    )
)


# ============================================================
# STEP 11: CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")

print(cm)


# ============================================================
# STEP 12: FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({

    "feature": feature_columns,

    "importance": model.feature_importances_

})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

# ============================================================
# STEP 14: SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "xgboost_freelancer_model.pkl"
)


print(
    "\nModel saved as:"
    " xgboost_freelancer_model.pkl"
)

# ============================================================
# STEP 15: CREATE TEST RESULT FILE
# ============================================================

test_results = df.loc[
    X_test.index
].copy()

test_results[
    "predicted_label"
] = y_pred

test_results[
    "recommendation_probability"
] = y_probability


test_results.to_csv(
    "data/xgboost_test_results.csv",
    index=False
)


print(
    "\nTest predictions saved as:"
    " data/xgboost_test_results.csv"
)

print("\nTRAINING PIPELINE COMPLETED")