import pickle
import logging
import os
from django.conf import settings
from sklearn import __version__ as sklearn_version

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

        model_path = settings.LOCAL_MODEL_PATH

        # Check if model exists locally, if not download it
        if not os.path.exists(model_path):
            logger.warning("Model file not found locally, attempting to download from blob storage...")
            from core.livenews.model_utils import download_model_from_blob
            if not download_model_from_blob():
                raise FileNotFoundError("Failed to download model from blob storage. Please check your storage settings.")

        # Load the model
        with open(model_path, "rb") as f:
            loaded_object = pickle.load(f)

        # Determine if the loaded object is a dictionary (newer format) or a single model (older format)
        if isinstance(loaded_object, dict):
            logger.info("Loaded object is a dictionary, extracting model and vectorizer...")
            model = loaded_object.get("model")
            vectorizer = loaded_object.get("vectorizer")
            saved_version = loaded_object.get("sklearn_version", "unknown")

            if model is None:
                raise ValueError("Model not found in the loaded dictionary.")
        else:
            logger.info("Loaded object is a single model (older format, without vectorizer).")
            model = loaded_object
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
