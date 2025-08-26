"""
Application configuration settings
"""
import os
from pathlib import Path

# Base directory (parent of config)
BASE_DIR = Path(__file__).parent.parent.absolute()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    DEBUG = False
    TESTING = False
    
    # Data directories
    DATA_DIR = BASE_DIR / 'data'
    PRODUCTION_DATA_DIR = DATA_DIR / 'production'
    TEST_DATA_DIR = DATA_DIR / 'test'
    
    # Ensure data directories exist
    PRODUCTION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Flask settings
    HOST = '0.0.0.0'
    PORT = 5001
    
    # Application settings
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    
    def __init__(self):
        # Check secret key requirement for production at runtime
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        self.SECRET_KEY = secret_key

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Use test data directory by default
    DEFAULT_DATA_DIR = Config.TEST_DATA_DIR

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    return config[config_name]