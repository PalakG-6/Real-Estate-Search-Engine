import pandas as pd
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import PyPDF2
import requests
from io import BytesIO
import config
import uuid
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize embedding model
logging.info("Loading embedding model...")
embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
logging.info("Model loaded successfully!")

def create_mysql_engine():
    """Create SQLAlchemy engine for MySQL"""
    try:
        connection_string = (
            f"mysql+mysqlconnector://{config.MYSQL_CONFIG['user']}:"
            f"{config.MYSQL_CONFIG['password']}@{config.MYSQL_CONFIG['host']}:"
            f"{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']}"
        )
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        logging.error(f"Error creating MySQL engine: {e}")
        return None

def setup_mysql_database():
    """Create database and tables"""
    try:
        # First connect without database to create it
        connection_string = (
            f"mysql+mysqlconnector://{config.MYSQL_CONFIG['user']}:"
            f"{config.MYSQL_CONFIG['password']}@{config.MYSQL_CONFIG['host']}:"
            f"{config.MYSQL_CONFIG['port']}"
        )
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            # Create database if not exists
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_CONFIG['database']}"))
            conn.commit()
        
        logging.info(f"✓ Database '{config.MYSQL_CONFIG['database']}' created/verified!")
        
        # Now connect to the database and create tables
        engine = create_mysql_engine()
        
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
        
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
        
        logging.info("✓ MySQL tables created successfully!")
        return engine
        
    except Exception as e:
        logging.error(f"Error setting up MySQL database: {e}")
        return None

def setup_qdrant():
    """Initialize Qdrant vector database (Cloud or Local)"""
    try:
        # Use cloud configuration if available
        if config.QDRANT_URL and config.QDRANT_API_KEY:
            client = QdrantClient(
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY,
            )
            logging.info("Connected to Qdrant Cloud")
        else:
            # Use local configuration
            client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
            logging.info("Connected to local Qdrant")
        
        # Get embedding dimension
        sample_embedding = embedding_model.encode("sample text")
        vector_size = len(sample_embedding)
        
        # Create collection if not exists
        collections = client.get_collections().collections
        collection_exists = any(c.name == config.QDRANT_COLLECTION for c in collections)
        
        if not collection_exists:
            client.create_collection(
                collection_name=config.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logging.info(f"Qdrant collection '{config.QDRANT_COLLECTION}' created successfully!")
        else:
            logging.info(f"Qdrant collection '{config.QDRANT_COLLECTION}' already exists!")
        
        return client
    except Exception as e:
        logging.error(f"Error setting up Qdrant: {e}")
        return None

def extract_pdf_text(url):
    """Extract text from PDF URL"""
    try:
        response = requests.get(url, timeout=10)
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text.strip()
    except Exception as e:
        logging.warning(f"Error extracting PDF from {url}: {e}")
        return ""

def clean_dataframe(df):
    """Clean and prepare dataframe for ingestion"""
    # Generate property_id if not exists
    if 'property_id' not in df.columns:
        df['property_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Fill missing values
    numeric_columns = ['price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Fill string columns
    string_columns = ['title', 'long_description', 'location', 'city', 'state', 
                     'zipcode', 'property_type', 'status', 'agent_name', 'agent_contact']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')
    
    # Set default status if not exists
    if 'status' not in df.columns or df['status'].isna().all():
        df['status'] = 'Active'
    
    return df

def ingest_to_mysql(df, engine):
    """Insert property data into MySQL using pandas to_sql"""
    try:
        # Clean the dataframe
        df_clean = clean_dataframe(df.copy())
        
        # Select only the columns we need
        columns_to_insert = [
            'property_id', 'title', 'long_description', 'location', 'city', 
            'state', 'zipcode', 'price', 'bedrooms', 'bathrooms', 'square_feet',
            'lot_size', 'year_built', 'property_type', 'listing_date', 'status',
            'agent_name', 'agent_contact', 'inspection_report_url', 'certificate_url'
        ]
        
        # Keep only columns that exist in the dataframe
        existing_columns = [col for col in columns_to_insert if col in df_clean.columns]
        df_to_insert = df_clean[existing_columns]
        
        # Use pandas to_sql
        df_to_insert.to_sql(
            'properties', 
            con=engine, 
            if_exists='replace',
            index=False
        )
        
        logging.info(f"✓ Inserted {len(df_to_insert)} properties into MySQL!")
        return len(df_to_insert)
        
    except Exception as e:
        logging.error(f"Error inserting data to MySQL: {e}")
        return 0

def ingest_to_qdrant(df, qdrant_client):
    """Insert property embeddings into Qdrant"""
    points = []
    
    for idx, row in df.iterrows():
        try:
            # Combine text fields for embedding
            title = str(row.get('title', ''))
            description = str(row.get('long_description', ''))
            location = str(row.get('location', ''))
            
            text_content = f"{title} {description} {location}"
            
            # Add PDF content if URL exists
            if pd.notna(row.get('inspection_report_url')):
                pdf_text = extract_pdf_text(row['inspection_report_url'])
                if pdf_text:
                    text_content += f" {pdf_text[:1000]}"
            
            # Generate embedding
            embedding = embedding_model.encode(text_content).tolist()
            
            # Create point with metadata
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    'property_id': str(row.get('property_id', '')),
                    'title': title[:500],
                    'description': description[:1000],
                    'location': location,
                    'city': str(row.get('city', '')),
                    'price': float(row.get('price', 0)),
                    'bedrooms': int(row.get('bedrooms', 0)),
                    'property_type': str(row.get('property_type', ''))
                }
            )
            points.append(point)
            
        except Exception as e:
            logging.warning(f"Error processing row {idx}: {e}")
            continue
    
    # Upload to Qdrant in batches
    if points:
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            qdrant_client.upsert(
                collection_name=config.QDRANT_COLLECTION,
                points=batch
            )
        
        logging.info(f"Inserted {len(points)} property embeddings into Qdrant!")
    
    return len(points)

def main(excel_file_path):
    """Main ingestion pipeline"""
    print("\n" + "=" * 70)
    print(" " * 15 + "REAL ESTATE DATA INGESTION PIPELINE")
    print("=" * 70 + "\n")
    
    # Step 1: Read Excel file
    logging.info("[1/5] Reading Excel file...")
    try:
        # Try reading as xlsx first, then csv
        if excel_file_path.endswith('.csv'):
            df = pd.read_csv(excel_file_path)
        else:
            df = pd.read_excel(excel_file_path)
        
        logging.info(f"Loaded {len(df)} properties from file")
        logging.info(f"Columns found: {list(df.columns)}")
        print(f"\n Loaded {len(df)} rows")
        print(f"Columns: {', '.join(list(df.columns)[:5])}...")
        
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        print(f"\n✗ Error reading file: {e}")
        return
    
    # Step 2: Setup MySQL
    logging.info("\n[2/5] Setting up MySQL database...")
    engine = setup_mysql_database()
    if engine is None:
        print("\nFailed to setup MySQL. Please check your credentials in .env file")
        return
    
    # Step 3: Setup Qdrant
    logging.info("\n[3/5] Setting up Qdrant vector database...")
    qdrant_client = setup_qdrant()
    if qdrant_client is None:
        print("\n✗ Failed to setup Qdrant. Check your configuration!")
        return
    
    # Step 4: Ingest to MySQL
    logging.info("\n[4/5] Ingesting data to MySQL...")
    mysql_count = ingest_to_mysql(df, engine)
    
    # Step 5: Ingest to Qdrant
    logging.info("\n[5/5] Ingesting data to Qdrant (generating embeddings)...")
    qdrant_count = ingest_to_qdrant(df, qdrant_client)
    
    print("\n" + "=" * 70)
    print(" " * 20 + " INGESTION COMPLETED!")
    print("=" * 70)
    print(f"\n  MySQL Records: {mysql_count}")
    print(f"  Qdrant Vectors: {qdrant_count}")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    # Specify your Excel file path
    excel_file = "/home/palak/Desktop/Palak/Real_estate_search/Property_list.xlsx"  
    main(excel_file)