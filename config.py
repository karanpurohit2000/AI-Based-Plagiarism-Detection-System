# config.py (updated)
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    # Academic placeholder
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    
    # Google services configuration
    GOOGLE_VISION_CREDS = os.path.join(Path(__file__).parent, "secrets/vision-service-account.json")
    GOOGLE_NLP_CREDS = os.path.join(Path(__file__).parent, "secrets/nlp-service-account.json")
    GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
    
    # System parameters
    MAX_FILE_SIZE = 50  # MB
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]
    REQUIRED_DIRS = ["data", "uploads", "reports", "secrets"]

    @classmethod
    def validate_paths(cls):
        """Validate all required credentials and directories"""
        missing = []
        
        # Check credential files
        if not os.path.exists(cls.GOOGLE_VISION_CREDS):
            missing.append(f"Vision credentials: {cls.GOOGLE_VISION_CREDS}")
        if not os.path.exists(cls.GOOGLE_NLP_CREDS):
            missing.append(f"NLP credentials: {cls.GOOGLE_NLP_CREDS}")
            
        # Check environment variables
        if not cls.GOOGLE_SEARCH_KEY:
            missing.append("GOOGLE_SEARCH_KEY environment variable")
        if not cls.GOOGLE_CSE_ID:
            missing.append("GOOGLE_CSE_ID environment variable")
        
        # Create directories if missing
        for directory in cls.REQUIRED_DIRS:
            os.makedirs(directory, exist_ok=True)
        
        # Raise error if any missing items
        if missing:
            error_msg = "Missing required configuration:\n- " + "\n- ".join(missing)
            raise RuntimeError(error_msg)
        
        # Set Google credentials environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cls.GOOGLE_NLP_CREDS