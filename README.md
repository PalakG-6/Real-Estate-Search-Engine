# Real Estate Search Engine

Multi-Agent AI System for Intelligent Property Search

---

## Overview

This system uses 8 specialized AI agents to provide intelligent property search, market analysis, and automated reporting capabilities. Users can search properties using natural language, get renovation cost estimates, and generate professional PDF reports.

---

## Features

- Natural language property search
- Semantic search using vector embeddings
- Automated PDF report generation with charts
- Renovation cost estimation
- Persistent user memory across sessions
- Multi-page web interface

---

## System Architecture
<img width="3387" height="1151" alt="Model_Architecture (2)" src="https://github.com/user-attachments/assets/05759a26-5391-4cc8-9075-65ee1a8257c6" />

---

## Technology Stack

**Backend:** Python 3.10, MySQL, Qdrant, SQLAlchemy  
**AI/ML:** Sentence Transformers, Vector Search  
**Frontend:** Streamlit, Plotly, Matplotlib  
**Reports:** ReportLab, Pandas  

---

For DATABASE_SCHEMA.md go to docs->DATABASE_SCHEMA.md

For DEPLOYMENT.md go to docs->DEPLOYMENT.md

For the task presentation go to docs->Real_Estate_Presentation.pptx

For the video walkthrough go to docs->Process_Walkthrough.mp4


## Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher


### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/real-estate-search.git
cd real-estate-search
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL

**Start MySQL:**
```bash
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS
net start MySQL80          # Windows
```

**Create Database:**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE real_estate_db;
EXIT;
```

### Step 5: Setup Qdrant (Cloud)

1. Sign up at https://cloud.qdrant.io (free tier available)
2. Create a cluster
3. Copy cluster URL and API key

### Step 6: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

**Update .env with your values:**
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=real_estate_db

QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_api_key
```

### Step 7: Initialize Database

```bash
python scripts/setup_db.py
```
Change path to you data folder here in ingest_data.py:
excel_file = "your_path/Property_list.xlsx"  

### Step 8: Run Application

```bash
streamlit run Home.py
```

Open browser: http://localhost:8501

---

## Usage

### 1. Upload Data

- Go to "Data Ingestion" page
- Upload Excel/CSV file with property data
- Click "Start Ingestion"

**Required columns:** property_id, location, price, long_description, listing_date, status

### 2. Search Properties

Go to "Chat" page and type queries like:

```
"Show statistics"
"Generate report"
"Properties in Hyderabad"
"Properties under 25000000"
"Find properties in Hyderabad and estimate renovation costs"
"Estimate renovation for 1500 sq ft"
```

### 3. Generate Reports

After searching:
- Click "Generate PDF Report"
- Download the generated PDF

### 4. Get Cost Estimates

```
"Estimate renovation for 1500 sq ft"
```


## Project Structure

```
real-estate-search/
├── Home.py                  # Main entry point
├── config.py               # Configuration
├── agents/                 # AI agents
│   ├── query_router.py
│   ├── task_planner.py
│   ├── structured_data_agent.py
│   ├── rag_agent.py
│   ├── web_research_agent.py
│   ├── report_agent.py
│   ├── renovation_agent.py
│   └── memory.py
├── pages/                  # Streamlit pages
│   ├── 1_Data_Ingestion.py
│   └── 2_Chat.py
├── ETL scripts/               # Setup scripts
│   ├── ingest_data.py
│   └── setup_db.py
├── data/                  # Data files
├── reports/              # Generated reports
├── logs/                 # Application logs
├── docs/                 # Documentation
├── requirements.txt      # Dependencies
├── .env.example         # Configuration template
└── README.md           # This file
```

---

