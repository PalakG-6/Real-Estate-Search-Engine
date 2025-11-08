import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'real_estate_db')
}

# Qdrant Configuration
QDRANT_URL = os.getenv('QDRANT_URL', None)
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', None)
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
QDRANT_COLLECTION = 'properties'

# Embedding Model
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'