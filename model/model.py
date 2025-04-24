import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib

def train_dataset(dataset_path):
    """
    train_dataset(dataset_path)

    Trains a text classification model using a provided dataset. The function reads the dataset
    from a CSV file, splits it into training and testing subsets, creates a classification
    pipeline with TF-IDF vectorization and Logistic Regression, trains the model, and saves
    the trained model to a file.

    Parameters:
        dataset_path (str): The file path to the dataset in CSV format. The dataset should
        contain two columns: 'prompt' for text input and 'label' for classification labels.

    Raises:
        FileNotFoundError: Raised if the specified dataset_path does not exist or is inaccessible.
    """
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
    """
    Get a filtered collection of labels based on their probability predictions.

    This function takes a model, a text prompt, and a threshold value to determine
    which labels are included in the returned collection. It predicts the
    probability of each label for the given prompt, sorts them by descending
    probability, and filters out labels whose probability falls below the
    provided threshold value. If no labels meet the threshold, the top three
    predicted labels are returned instead.

    Arguments:
        model: The model object that includes a `predict_proba` method for generating
            probability predictions and a `classes_` attribute that provides a list
            of label names.
        prompt (str): The text prompt provided by the user for which probabilities
            are to be predicted.
        threshold (float, optional): The minimum probability value a label must have
            to be included in the filtered list. Default is 0.5.

    Returns:
        list: A list of labels, filtered by probability threshold. If no labels meet
        the threshold, the top three predicted labels are returned.
    """
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
