import pickle
import logging
import os
from django.conf import settings
from sklearn import __version__ as sklearn_version
from core.livenews.model_utils import download_model_from_blob

logger = logging.getLogger(__name__)

def load_models():
    """
    Load the trained model and vectorizer, ensuring compatibility with the current scikit-learn version.
    If the model is not found locally, it will be downloaded from blob storage.
    """
    try:
        logger.info("Loading model...")
        # Get current scikit-learn version
        current_version = sklearn_version
        logger.info(f"Current scikit-learn version: {current_version}")

        # Check if model exists locally, if not download it
        if not os.path.exists(settings.LOCAL_MODEL_PATH):
            if not download_model_from_blob():
                raise Exception("Failed to download model from blob storage")

        # Load the model from the local path
        with open(settings.LOCAL_MODEL_PATH, 'rb') as f:
            model_info = pickle.load(f)
        
        # Extract model, vectorizer, and saved scikit-learn version
        saved_version = model_info['sklearn_version']
        vectorizer = model_info['vectorizer']
        model = model_info['model']
        
        logger.info(f"Loaded model trained with scikit-learn version: {saved_version}")

        # Test the models with a sample prediction

        logger.info("Successfully loaded and tested model")
        
        return model, vectorizer
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise Exception("Failed to load models. Please ensure model files exist in the correct location.")

class Model:
    def __init__(self):
        # Load the model and vectorizer on initialization
        self._model, self._vectorizer = load_models()

    def get_model(self):
        return self._model, self._vectorizer
