import os
from typing import Dict, Any
from pydantic import BaseModel

class AgencyBranding(BaseModel):
    name: str = "EduGlobal Media & Verification"
    tagline: str = "Verified University Media Intelligence"
    contact_email: str = "audit@eduglobal.io"
    website: str = "https://eduglobal.io"
    primary_color: str = "#2563eb" # Blue
    secondary_color: str = "#0f172a" # Slate dark
    accent_color: str = "#10b981" # Emerald

class Settings(BaseModel):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MAPILLARY_CLIENT_TOKEN: str = os.getenv("MAPILLARY_CLIENT_TOKEN", "")
    GOOGLE_CSE_API_KEY: str = os.getenv("GOOGLE_CSE_API_KEY", "")
    GOOGLE_CSE_CX: str = os.getenv("GOOGLE_CSE_CX", "")
    
    API_TIMEOUT_SECONDS: float = 5.0
    WEB_SEARCH_TIMEOUT: float = 4.0
    MAX_IMAGES_PER_CAMPUS: int = 30
    TARGET_IMAGE_SIZE: int = 224
    PHASH_HAMMING_THRESHOLD: int = 6
    CONFIDENCE_THRESHOLD: float = 0.65
    TORCH_THREADS: int = 4
    
    branding: AgencyBranding = AgencyBranding()

settings = Settings()
