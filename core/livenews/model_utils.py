import os
import logging
from azure.storage.blob import BlobServiceClient
from django.core import settings

logger = logging.getLogger(__name__)

def download_model_from_blob():
    """
    Downloads the model file from Azure Blob Storage if it doesn't exist locally.
    """
    # Check if model already exists locally
    if os.path.exists(settings.LOCAL_MODEL_PATH):
        logger.info("Model file already exists locally")
        return True

    try:
        # Ensure the models directory exists
        os.makedirs(os.path.dirname(settings.LOCAL_MODEL_PATH), exist_ok=True)

        # Initialize the blob service client
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        
        # Get container client
        container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)
        
        # Get blob client
        blob_client = container_client.get_blob_client(settings.MODEL_BLOB_NAME)

        logger.info(f"Downloading model from blob storage: {settings.MODEL_BLOB_NAME}")
        
        # Download the blob
        with open(settings.LOCAL_MODEL_PATH, "wb") as model_file:
            download_stream = blob_client.download_blob()
            model_file.write(download_stream.readall())

        logger.info("Model downloaded successfully")
        return True

    except Exception as e:
        logger.error(f"Error downloading model from blob storage: {str(e)}")
        return False