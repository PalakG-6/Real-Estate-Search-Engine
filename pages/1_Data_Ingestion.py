"""
Data Ingestion Page - Upload and process property data
"""
import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import config
import uuid
import logging

st.set_page_config(page_title="Data Ingestion", page_icon="📊", layout="wide")

st.title("Data Ingestion")
st.markdown("Upload your property data Excel file to add properties to the database.")

# Initialize components
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(config.EMBEDDING_MODEL)

@st.cache_resource
def get_qdrant_client():
    if config.QDRANT_URL and config.QDRANT_API_KEY:
        return QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    return QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)

def create_mysql_engine():
    connection_string = (
        f"mysql+mysqlconnector://{config.MYSQL_CONFIG['user']}:"
        f"{config.MYSQL_CONFIG['password']}@{config.MYSQL_CONFIG['host']}:"
        f"{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']}"
    )
    return create_engine(connection_string)

def clean_dataframe(df):
    """Clean and prepare dataframe"""
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
    
    if 'status' not in df.columns or df['status'].isna().all():
        df['status'] = 'Active'
    
    return df

def ingest_to_mysql(df, engine, progress_bar):
    """Insert data into MySQL"""
    try:
        df_clean = clean_dataframe(df.copy())
        columns_to_insert = [
            'property_id', 'title', 'long_description', 'location', 'city', 
            'state', 'zipcode', 'price', 'bedrooms', 'bathrooms', 'square_feet',
            'lot_size', 'year_built', 'property_type', 'listing_date', 'status',
            'agent_name', 'agent_contact', 'inspection_report_url', 'certificate_url'
        ]
        
        existing_columns = [col for col in columns_to_insert if col in df_clean.columns]
        df_to_insert = df_clean[existing_columns]
        
        progress_bar.progress(50, "Inserting into MySQL...")
        df_to_insert.to_sql('properties', con=engine, if_exists='append', index=False)
        
        return len(df_to_insert), None
    except Exception as e:
        return 0, str(e)

def ingest_to_qdrant(df, qdrant_client, model, progress_bar):
    """Insert embeddings into Qdrant"""
    points = []
    
    for idx, row in df.iterrows():
        try:
            title = str(row.get('title', ''))
            description = str(row.get('long_description', ''))
            location = str(row.get('location', ''))
            text_content = f"{title} {description} {location}"
            
            embedding = model.encode(text_content).tolist()
            
            point = PointStruct(
                id=len(points),
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
            
            if (idx + 1) % 10 == 0:
                progress_percent = 50 + int((idx + 1) / len(df) * 50)
                progress_bar.progress(progress_percent, f"Processing embeddings... {idx+1}/{len(df)}")
        except Exception as e:
            continue
    
    if points:
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            qdrant_client.upsert(
                collection_name=config.QDRANT_COLLECTION,
                points=batch
            )
    
    return len(points), None

# Main UI
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file (XLSX or CSV)",
    type=['xlsx', 'xls', 'csv'],
    help="Upload your property data file"
)

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"File loaded successfully! Found {len(df)} rows.")
        
        # Show preview
        with st.expander("Preview Data (First 5 rows)"):
            st.dataframe(df.head())
        
        # Show columns
        with st.expander("Column Information"):
            st.write(f"**Total Columns:** {len(df.columns)}")
            st.write("**Columns:**")
            for col in df.columns:
                st.write(f"- {col}")
        
        # Ingestion button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Ingestion", type="primary", use_container_width=True):
                # Create progress bar
                progress_bar = st.progress(0, "Starting ingestion...")
                status_text = st.empty()
                
                try:
                    # Load model and clients
                    status_text.info("Loading embedding model...")
                    model = load_embedding_model()
                    progress_bar.progress(10, "Loading embedding model...")
                    
                    status_text.info("Connecting to databases...")
                    engine = create_mysql_engine()
                    qdrant_client = get_qdrant_client()
                    progress_bar.progress(20, "Connected to databases...")
                    
                    # Ingest to MySQL
                    status_text.info("Inserting data into MySQL...")
                    mysql_count, mysql_error = ingest_to_mysql(df, engine, progress_bar)
                    
                    if mysql_error:
                        st.error(f"MySQL Error: {mysql_error}")
                    else:
                        progress_bar.progress(60, "MySQL ingestion complete...")
                        
                        # Ingest to Qdrant
                        status_text.info("Creating embeddings and inserting into Qdrant...")
                        qdrant_count, qdrant_error = ingest_to_qdrant(df, qdrant_client, model, progress_bar)
                        
                        if qdrant_error:
                            st.error(f"Qdrant Error: {qdrant_error}")
                        else:
                            progress_bar.progress(100, "Ingestion complete!")
                            status_text.empty()
                            
                            # Success message
                            st.balloons()
                            st.success("Ingestion Completed Successfully!")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("MySQL Records", mysql_count)
                            with col_b:
                                st.metric("Qdrant Vectors", qdrant_count)
                            
                            st.info("Your properties are now searchable in the chatbot!")
                
                except Exception as e:
                    st.error(f"Error during ingestion: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()
    
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.info("Please make sure your file is a valid Excel or CSV file.")

else:
    st.info("👆 Please upload an Excel file to begin.")
    
    # Show example format
    with st.expander("Expected File Format"):
        st.markdown("""
        Your Excel file should contain the following columns (minimum):
        
        **Required Columns:**
        - `title` or `short_description`: Property title
        - `long_description`: Detailed description
        - `location`: Property location
        - `price`: Property price
        
        **Optional Columns:**
        - `property_id`: Unique identifier (auto-generated if missing)
        - `city`: City name
        - `state`: State name
        - `zipcode`: ZIP/Postal code
        - `bedrooms` or `num_rooms`: Number of bedrooms
        - `bathrooms`: Number of bathrooms
        - `square_feet` or `property_size_sqft`: Property size
        - `property_type`: Type (apartment, house, villa, etc.)
        - `listing_date`: Date listed
        - `status`: Active, Sold, etc.
        - `agent_name`: Agent name
        - `agent_contact`: Contact information
        """)

# Database status
st.markdown("---")
st.subheader(" Database Connection Status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**MySQL**")
    try:
        engine = create_mysql_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM properties"))
            count = result.fetchone()[0]
            st.success(f"Connected - {count} properties")
    except Exception as e:
        st.error(f"Connection failed: {str(e)[:50]}...")

with col2:
    st.markdown("**Qdrant**")
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        if any(c.name == config.QDRANT_COLLECTION for c in collections):
            collection_info = client.get_collection(config.QDRANT_COLLECTION)
            st.success(f"Connected - {collection_info.points_count} vectors")
        else:
            st.warning("Collection not found")
    except Exception as e:
        st.error(f"Connection failed: {str(e)[:50]}...")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** You can upload multiple files. Each upload will append new properties to the database.")
