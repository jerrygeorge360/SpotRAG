import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib

def train_dataset(dataset_path):
    # Load dataset
    df = pd.read_csv(dataset_path)


    # Split
    X_train, X_test, y_train, y_test = train_test_split(df["prompt"], df["label"], test_size=0.2)

    # Create pipeline
    model = make_pipeline(TfidfVectorizer(), LogisticRegression())
    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "prompt_classifier.joblib")


def get_collection_from_prompt(model,prompt: str, threshold: float = 0.5):
    # Get the probability predictions for the prompt
    probs = model.predict_proba([prompt])[0]

    # Get label names
    labels = model.classes_

    # Pair each label with its probability
    label_probs = list(zip(labels, probs))

    # Sort by probability, descending
    sorted_labels = sorted(label_probs, key=lambda x: x[1], reverse=True)

    # Filter out intents that have a probability below the threshold
    print(sorted_labels)
    filtered_labels = [label for label, prob in sorted_labels if prob >= threshold]
    if not filtered_labels:
        return sorted_labels[:3]

    return filtered_labels
