import pickle
import logging
import os
import numpy as np
from django.conf import settings
from sklearn import __version__ as sklearn_version

logger = logging.getLogger(__name__)

def load_models():
    """
    Load the trained model and vectorizer
    """
    try:
        logger.info("Loading model...")
        
        # Check if model exists locally, if not download it
        if not os.path.exists(settings.LOCAL_MODEL_PATH):
            logger.info("Model not found locally, downloading from blob storage...")
            from core.livenews.model_utils import download_model_from_blob
            if not download_model_from_blob():
                raise Exception("Failed to download model from blob storage")
        
        # Load the model
        with open(settings.LOCAL_MODEL_PATH, 'rb') as f:
            models = pickle.load(f)
            
        nb_model = models['model']
        vect_model = models['vectorizer']
        
        # Test the model
        test_text = "This is a test article"
        features = vect_model.transform([test_text])
        prediction = nb_model.predict(features)
        probabilities = nb_model.predict_proba(features)
        
        logger.info("Model test results:")
        logger.info(f"- Test prediction: {prediction[0]}")
        logger.info(f"- Test probability: {probabilities[0][1]:.2%}")
        logger.info(f"- Vectorizer vocabulary size: {len(vect_model.vocabulary_)}")
        
        return nb_model, vect_model
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

class Model:
    def __init__(self):
        self._model, self._vectorizer = load_models()

    def get_model(self):
        return self._model, self._vectorizer
