"""
Configuration for Cloud Run deployment
"""
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings for Cloud Run deployment"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", "8080"))
    
    # LINE Bot Configuration
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    
    # AI Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Telegram Notifications (Optional)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "https://localhost:5173",
        "https://*.run.app",
        "https://*.vercel.app",
    ]
    
    # Additional allowed origins from environment
    if os.getenv("ALLOWED_ORIGINS"):
        allowed_origins.extend(os.getenv("ALLOWED_ORIGINS").split(","))
    
    # Security
    trusted_hosts: List[str] = ["*"]  # Cloud Run handles host validation
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Performance
    workers: int = int(os.getenv("WORKERS", "1"))
    worker_timeout: int = int(os.getenv("WORKER_TIMEOUT", "300"))
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def docs_enabled(self) -> bool:
        return self.is_development or self.debug
    
    def validate_required_vars(self) -> List[str]:
        """Validate required environment variables and return missing ones"""
        required_vars = {
            "LINE_CHANNEL_ACCESS_TOKEN": self.line_channel_access_token,
            "LINE_CHANNEL_SECRET": self.line_channel_secret,
            "GEMINI_API_KEY": self.gemini_api_key,
        }
        
        # Add Supabase vars if configured
        if self.supabase_url:
            required_vars["SUPABASE_ANON_KEY"] = self.supabase_anon_key
        
        return [var for var, value in required_vars.items() if not value]

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()