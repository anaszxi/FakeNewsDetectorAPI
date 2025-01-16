import pickle
import logging
import os
from django.conf import settings
from sklearn import __version__ as sklearn_version

logger = logging.getLogger(__name__)

def load_models():
    """Load the trained model and vectorizer."""
    try:
        logger.info("Loading model...")

        # Get current scikit-learn version
        current_version = sklearn_version
        logger.info(f"Current scikit-learn version: {current_version}")

        model_path = settings.LOCAL_MODEL_PATH

        # Check if model exists locally, if not download it
            
        # Load the model
        with open(model_path, "rb") as f:
            model_info = pickle.load(f)

        # Determine if the loaded object is a dictionary (newer format) or a single model (older format)
        if isinstance(model_info, dict):
            logger.info("Loaded object is a dictionary, extracting model and vectorizer...")
            model = model_info.get("model")
            vectorizer = model_info.get("vectorizer")
            saved_version = model_info.get("sklearn_version", "unknown")

            if model is None:
                raise ValueError("Model not found in the loaded dictionary.")
        else:
            logger.info("Loaded object is a single model (older format, without vectorizer).")
            model = model_info
            vectorizer = None
            saved_version = "unknown"

        # Check scikit-learn version compatibility
        logger.info(f"Model was trained with scikit-learn version: {saved_version}")
        if saved_version != "unknown" and saved_version != current_version:
            logger.warning(f"⚠️ Version mismatch: Model trained with {saved_version}, but current version is {current_version}. "
                           "This may cause compatibility issues.")

        logger.info("✅ Model successfully loaded.")
        return model, vectorizer

    except Exception as e:
        logger.error(f"❌ Error loading models: {str(e)}")
        raise Exception("Failed to load models. Ensure the model file exists and is correctly formatted.")

class Model:
    def __init__(self):
        """Initialize and load the trained model and vectorizer."""
        self._model, self._vectorizer = load_models()

    def get_model(self):
        """Return the loaded model and vectorizer."""
        return self._model, self._vectorizer
