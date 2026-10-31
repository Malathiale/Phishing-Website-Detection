
import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Load dataset
df = pd.read_csv("dataset/phishtrap_full.csv")

features = [
    "url_length",
    "hyphen_count",
    "digit_count",
    "subdomain_count",
    "trusted_tld",
    "protocol_exists",
    "special_char_count",
    "entropy",
    "path_depth",
    "domain_length",
    "is_domain_ip",
    "has_at_symbol",
    "has_double_slash_redirect",
    "tld_length",
    "query_param_count",
    "path_length"
]

# Clean dataset
df = df.drop_duplicates()
df = df.dropna(subset=features + ["label"])

X = df[features]
y = df["label"].astype(int)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

cm = confusion_matrix(y_test, predictions)

print("\nMODEL PERFORMANCE")
print("-----------------")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

print("Confusion Matrix:")
print(cm)

# Save model and evaluation results
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/phishing_model.pkl")
joblib.dump(features, "models/features.pkl")

metrics = {
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "confusion_matrix": cm,
    "test_samples": len(y_test)
}

joblib.dump(metrics, "models/metrics.pkl")

print("\nModel and evaluation metrics saved successfully!")
