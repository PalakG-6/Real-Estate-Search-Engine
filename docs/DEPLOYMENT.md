# Deployment Guide

Complete guide for deploying the Real Estate Search Engine in various environments.


## Prerequisites

### System Requirements
- **OS:** Linux (Ubuntu 20.04+), macOS 11+, or Windows 10+


### Software Requirements
- Python 3.10 or higher
- MySQL 8.0 or higher
- Git
- pip (Python package manager)

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/real-estate-search.git
cd real-estate-search
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Update these values in `.env`:**
```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=real_estate_db

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_api_key
```

### Step 5: Setup MySQL Database

**Start MySQL:**
```bash
# Linux
sudo systemctl start mysql

# macOS
brew services start mysql

# Windows
net start MySQL80
```

**Create Database:**
```bash
python scripts/setup_db.py
```

Or manually:
```sql
mysql -u root -p

CREATE DATABASE real_estate_db;
USE real_estate_db;
SOURCE scripts/schema.sql;
EXIT;
```

### Step 6: Setup Qdrant

1. Sign up at https://cloud.qdrant.io
2. Create a free cluster
3. Copy URL and API key to `.env`


### Step 7: Verify Setup

```bash
python scripts/verify_setup.py
```

Expected output:
```
Python version: 3.10.x
MySQL connection: OK
Qdrant connection: OK
All dependencies: OK
```

### Step 8: Run Application

```bash
streamlit run src/Home.py
```

Access at: `http://localhost:8501`

---




