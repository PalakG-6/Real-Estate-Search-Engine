"""
Database Setup Script
Initializes MySQL and Qdrant databases
"""
import mysql.connector
from mysql.connector import Error
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import config

def setup_mysql():
    """Setup MySQL database and tables"""
    print("Setting up MySQL...")
    
    try:
        # Connect without database
        connection = mysql.connector.connect(
            host=config.MYSQL_CONFIG['host'],
            port=config.MYSQL_CONFIG['port'],
            user=config.MYSQL_CONFIG['user'],
            password=config.MYSQL_CONFIG['password']
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_CONFIG['database']}")
        cursor.execute(f"USE {config.MYSQL_CONFIG['database']}")
        
        # Create properties table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS properties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            property_id VARCHAR(100) UNIQUE,
            title VARCHAR(500),
            long_description TEXT,
            location VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            zipcode VARCHAR(20),
            price DECIMAL(15, 2),
            bedrooms INT,
            bathrooms DECIMAL(3, 1),
            square_feet INT,
            lot_size DECIMAL(10, 2),
            year_built INT,
            property_type VARCHAR(100),
            listing_date DATE,
            status VARCHAR(50),
            agent_name VARCHAR(255),
            agent_contact VARCHAR(100),
            inspection_report_url TEXT,
            certificate_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_location (location),
            INDEX idx_price (price),
            INDEX idx_city (city),
            INDEX idx_property_type (property_type)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        
        print("✅ MySQL database and tables created successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"MySQL Error: {e}")
        return False

def setup_qdrant():
    """Setup Qdrant vector database"""
    print("\nSetting up Qdrant...")
    
    try:
        # Connect to Qdrant
        if config.QDRANT_URL and config.QDRANT_API_KEY:
            client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
            print("Connected to Qdrant Cloud")
        else:
            client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
            print("Connected to local Qdrant")
        
        # Get embedding dimension
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        sample_embedding = model.encode("sample text")
        vector_size = len(sample_embedding)
        
        # Create collection
        collections = client.get_collections().collections
        collection_exists = any(c.name == config.QDRANT_COLLECTION for c in collections)
        
        if not collection_exists:
            client.create_collection(
                collection_name=config.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"✅ Qdrant collection '{config.QDRANT_COLLECTION}' created!")
        else:
            print(f"✅ Qdrant collection '{config.QDRANT_COLLECTION}' already exists!")
        
        return True
        
    except Exception as e:
        print(f"Qdrant Error: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("DATABASE SETUP")
    print("=" * 50)
    print()
    
    # Setup MySQL
    mysql_success = setup_mysql()
    
    # Setup Qdrant
    qdrant_success = setup_qdrant()
    
    print()
    print("=" * 50)
    if mysql_success and qdrant_success:
        print("Setup Complete!")
        print("=" * 50)
        print()
        print("Next step: Run the application")
        print("Command: streamlit run Home.py")
    else:
        print("Setup Failed")
        print("=" * 50)
        print()
        print("Please check your configuration in .env file")

if __name__ == "__main__":
    main()
