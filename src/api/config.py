import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME', 'smartcatalog')
DB_HOST = os.getenv('DB_HOST', 'localhost')

# For Cloud SQL, use unix socket
if os.getenv('K_SERVICE'):  # We're on Cloud Run
    socket_dir = '/cloudsql'
    cloud_sql_connection_name = 'key-being-442223-h1:europe-west1:smartcatalog-db'
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={socket_dir}/{cloud_sql_connection_name}"
else:
    # Local development
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Cloud Storage
BUCKET_NAME = "smartcatalog-storage"