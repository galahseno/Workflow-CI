import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os

# ================================
# 🚀 Load Preprocessed Data
# ================================
data_path = "cardiovascular_disease_preprocessing.csv"
df = pd.read_csv(data_path)
print(f"✅ Loaded dataset: {df.shape}")

# ================================
# 🧪 Train-Test Split
# ================================
X = df.drop(columns=["cardio"])
y = df["cardio"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================================
# ⚙️ Setup MLflow Local Tracking
# ================================
mlflow.set_tracking_uri("file:///tmp/mlruns")
mlflow.set_experiment("Cardiovascular_Classifier")

# ================================
# 🚀 Train Model with autolog
# ================================
with mlflow.start_run():
    mlflow.sklearn.autolog()

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # 🔍 Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print("\n✅ Accuracy:", acc)
    print("\n📋 Classification Report:\n", report)

    # Log additional metrics (optional)
    mlflow.log_metric("accuracy", acc)
    mlflow.log_artifact("cardiovascular_disease_preprocessing.csv")
    input_example = X_test

    mlflow.sklearn.log_model(
        model,
        name="model",
        input_example=input_example
    )

print("\n✅ Model training completed. Launch UI with: mlflow ui --backend-store-uri /tmp/mlruns")