import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory containing config.py
current_dir = Path(__file__).parent

# Load environment-specific .env file
env = os.getenv('ENVIRONMENT', 'development')
# env_file = '.env.production' if env == 'production' else '.env'
env_file = current_dir / ('.env.production' if env == 'production' else '.env')
load_dotenv(env_file)

# Add debug logging
print(f"Loading config from: {env_file}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")

# Database configuration
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
ALLOW_ORIGINS = (
    ["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"]
    if STORAGE_TYPE == 'local'
    else ["https://key-being-442223-h1.web.app", "https://www.thesmartcatalog.com"]
)

# Database URL construction
if STORAGE_TYPE == 'cloud':
    # Cloud SQL requires special URL format using Unix socket
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={DB_HOST}"
else:
    # Local PostgreSQL connection
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Storage configuration
if STORAGE_TYPE == 'cloud':
    BUCKET_NAME = "smartcatalog-storage"
    PDF_STORAGE_PATH = None
else:
    BUCKET_NAME = None
    PDF_STORAGE_PATH = os.path.abspath("pdfs")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
