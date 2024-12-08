import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle
import os
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_text(text):
    """Preprocess text with additional cleaning steps."""
    if pd.isna(text):
        return ''
    
    # Convert to string
    text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Count exclamation marks and question marks
    exclaim_count = text.count('!')
    question_count = text.count('?')
    
    # Count words in ALL CAPS
    caps_count = len(re.findall(r'\b[A-Z]{2,}\b', text))
    
    # Add these as features
    text = text + f' _exclaim_{min(exclaim_count, 5)} _question_{min(question_count, 5)} _caps_{min(caps_count, 5)}'
    
    # Replace multiple punctuation with single
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    
    # Add spaces around punctuation
    text = re.sub(r'([!?.])', r' \1 ', text)
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text

def train_models(data_path=None):
    """Train models using scikit-learn 1.5.2."""
    try:
        if data_path is None:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "WELFake_Dataset.csv")
        
        logger.info(f"Using dataset at: {data_path}")
        
        # Load dataset
        logger.info("Loading dataset...")
        df = pd.read_csv(
            data_path,
            encoding='utf-8',
            index_col=0,
            on_bad_lines='skip',
            dtype={
                'title': str,
                'text': str,
                'label': str
            }
        )
        
        logger.info(f"Successfully loaded dataset with {len(df)} rows")
        
        # Clean the data
        logger.info("Cleaning dataset...")
        
        # Clean labels
        logger.info("Cleaning labels...")
        logger.info(f"Initial label values: {df['label'].value_counts().to_dict()}")
        
        def clean_label(x):
            if pd.isna(x):
                return None
            try:
                x = str(x).strip().lower()
                if x in ['0', '1', '0.0', '1.0']:
                    return int(float(x))
                else:
                    return None
            except (ValueError, TypeError):
                return None
        
        df['label'] = df['label'].apply(clean_label)
        
        logger.info(f"Label distribution after cleaning: {df['label'].value_counts().to_dict()}")
        logger.info(f"Null labels: {df['label'].isnull().sum()}")
        
        df = df.dropna(subset=['label'])
        
        logger.info(f"Dataset size after cleaning labels: {len(df)} rows")
        logger.info(f"Final label distribution: {df['label'].value_counts().to_dict()}")
        
        # Clean and combine text
        df['title'] = df['title'].fillna('')
        df['text'] = df['text'].fillna('')
        
        # Preprocess text with new features
        df['title'] = df['title'].apply(preprocess_text)
        df['text'] = df['text'].apply(preprocess_text)
        df['title_text'] = df['title'] + ' ' + df['text']
        
        # Get labels
        y = df['label'].values
        
        # Split data
        logger.info("Splitting dataset...")
        X_train, X_test, y_train, y_test = train_test_split(
            df['title_text'], y, test_size=0.33, random_state=53
        )

        # Initialize vectorizer with more features
        logger.info("Vectorizing text...")
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100000,  # Increased from 50000
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2),  # Added bigrams
            sublinear_tf=True,   # Apply sublinear scaling
            strip_accents='unicode',
            token_pattern=r'\b\w+\b'  # Keep single-letter words
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        # Train Naive Bayes with better smoothing
        logger.info("Training Naive Bayes model...")
        nb_classifier = MultinomialNB(alpha=0.1)  # Adjusted smoothing
        nb_classifier.fit(X_train_vec, y_train)
        nb_pred = nb_classifier.predict(X_test_vec)
        
        logger.info("\nNaive Bayes Performance:")
        nb_report = classification_report(y_test, nb_pred)
        logger.info(f"\n{nb_report}")

        # Train Random Forest with better parameters
        logger.info("Training Random Forest model...")
        rf_classifier = RandomForestClassifier(
            n_estimators=500,     # Increased from 300
            max_depth=30,         # Increased from 20
            min_samples_split=5,
            min_samples_leaf=2,   # Added minimum leaf size
            max_features='sqrt',  # Use sqrt of features
            class_weight='balanced',  # Handle imbalanced classes
            n_jobs=-1
        )
        rf_classifier.fit(X_train_vec, y_train)
        rf_pred = rf_classifier.predict(X_test_vec)
        
        logger.info("\nRandom Forest Performance:")
        rf_report = classification_report(y_test, rf_pred)
        logger.info(f"\n{rf_report}")

        # Save models
        logger.info("Saving models...")
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(models_dir, exist_ok=True)

        model_info = {
            'sklearn_version': '1.5.2',
            'vectorizer': vectorizer,
            'model': rf_classifier  # Using Random Forest as it performs better
        }
        
        with open(os.path.join(models_dir, "model_1_5_2.pkl"), "wb") as f:
            pickle.dump(model_info, f)

        logger.info("Training completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        return False

if __name__ == "__main__":
    train_models() 