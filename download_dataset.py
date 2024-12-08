import os
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_dataset():
    """Download the WELFake dataset from Kaggle."""
    try:
        # Check if dataset already exists
        if os.path.exists("WELFake_Dataset.csv"):
            logger.info("Dataset already exists")
            return True
            
        logger.info("Downloading WELFake dataset from Kaggle...")
        
        # Create .kaggle directory if it doesn't exist
        kaggle_dir = os.path.expanduser("~/.kaggle")
        os.makedirs(kaggle_dir, exist_ok=True)
        
        # Download dataset using kaggle CLI
        subprocess.run([
            "kaggle",
            "datasets",
            "download",
            "-d",
            "saurabhshahane/fake-news-classification",
            "--unzip"
        ], check=True)
        
        logger.info("Dataset downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        logger.error("Please ensure you have:")
        logger.error("1. Installed kaggle package (pip install kaggle)")
        logger.error("2. Created a Kaggle account and downloaded your API token")
        logger.error("3. Placed your kaggle.json file in ~/.kaggle/")
        return False

if __name__ == "__main__":
    download_dataset() 