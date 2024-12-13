from django.conf import settings
import os
import pickle
import logging
import numpy as np
from sklearn import __version__ as sklearn_version

logger = logging.getLogger(__name__)

def load_models():
    """Load the trained models from pickle files."""
    try:
        # Get current scikit-learn version
        current_version = sklearn_version
        logger.info(f"Current scikit-learn version: {current_version}")
        
        # Define model paths
        model_path = os.path.join(settings.BASE_DIR, "models", "model_1_5_2.pkl")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load model info
        with open(model_path, "rb") as f:
            model_info = pickle.load(f)
            
        # Extract components
        saved_version = model_info['sklearn_version']
        vectorizer = model_info['vectorizer']
        model = model_info['model']
        
        logger.info(f"Loaded model trained with scikit-learn version: {saved_version}")
        
        if saved_version != current_version:
            logger.warning(f"Version mismatch: Model trained with {saved_version}, "
                         f"current version is {current_version}")
        
        # Test the models with a sample prediction
        test_text = "This is a test news article"
        test_features = vectorizer.transform([test_text])
        test_pred = model.predict(test_features)
        test_prob = model.predict_proba(test_features)
        
        logger.info("Model test results:")
        logger.info(f"- Test prediction: {test_pred[0]}")
        logger.info(f"- Test probability: {np.max(test_prob[0]):.2%}")
        logger.info(f"- Vectorizer vocabulary size: {len(vectorizer.vocabulary_)}")
        logger.info("Successfully loaded and tested model")
        
        return model, vectorizer
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise Exception("Failed to load models. Please ensure model files exist in the correct location.")