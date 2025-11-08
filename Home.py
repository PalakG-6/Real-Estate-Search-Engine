"""
Real Estate Search Engine - Home Page
"""
# http://localhost:8501
import streamlit as st

st.set_page_config(
    page_title="Real Estate Search Engine",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("Real Estate Search Engine")
st.markdown("Multi-Agent AI System for Intelligent Property Search")

st.markdown("---")

# Simple description
st.markdown("""
This system uses multiple AI agents to help you search, analyze, and generate reports 
about real estate properties. Upload your data, search for properties, and get instant 
insights with automated reports.
""")


st.markdown("---")

# Quick Start Guide
st.subheader("Quick Start")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**First Time?**")
    st.markdown("1. Go to Data Ingestion")
    st.markdown("2. Upload your Excel file")
    st.markdown("3. Click Start Ingestion")

with col2:
    st.markdown("**Already Have Data?**")
    st.markdown("1. Go to Chat page")
    st.markdown("2. Type your query")
    st.markdown("3. Get instant results")

with col3:
    st.markdown("**Need Help?**")
    st.markdown("Use natural language queries like:")
    st.markdown("- Show all properties")
    st.markdown("- Properties under 30000000")
    st.markdown("- Generate report")

st.markdown("---")

# System Architecture
st.subheader("System Architecture")

# Display the architecture diagram image
st.image("docs/Model_Architecture.png", use_column_width=True)

st.markdown("---")

# Agent Architecture
st.subheader("Agent Architecture")

# Display the architecture diagram image
st.image("docs/Agent_Architecture.png", use_column_width=True)

st.markdown("---")

# st.markdown("""
# ```mermaid
# graph TB
#     A[User Interface - Streamlit] --> B[Agent Layer]
#     B --> C[Query Router]
#     B --> D[Task Planner]
#     B --> E[Search Agents]
#     B --> F[Report Agent]
#     B --> G[Memory Manager]
    
#     E --> H[Structured Data Agent]
#     E --> I[RAG Agent]
    
#     H --> J[(MySQL Database)]
#     I --> K[(Qdrant Vector DB)]
#     F --> L[PDF Reports]
#     G --> M[JSON Storage]
    
#     style A fill:#e1f5ff
#     style B fill:#fff9e1
#     style J fill:#ffe1e1
#     style K fill:#ffe1e1
#     style L fill:#e1ffe1
#     style M fill:#ffe1e1
# ```
# """)

# st.markdown("---")

st.caption("Real Estate Search Engine")



