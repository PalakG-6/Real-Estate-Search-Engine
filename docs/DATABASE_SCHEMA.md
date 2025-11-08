# Database Schema Documentation

## Overview

The Real Estate Search Engine uses a dual-database architecture:
1. **MySQL** - For structured property data
2. **Qdrant** - For vector embeddings and semantic search

---

## MySQL Schema

### Properties Table

```sql
CREATE TABLE properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,
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
    status VARCHAR(50) DEFAULT 'Active',
    agent_name VARCHAR(255),
    agent_contact VARCHAR(100),
    inspection_report_url TEXT,
    certificate_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_property_id (property_id),
    INDEX idx_location (location),
    INDEX idx_city (city),
    INDEX idx_price (price),
    INDEX idx_property_type (property_type),
    INDEX idx_status (status),
    INDEX idx_listing_date (listing_date)
);
```

### Field Descriptions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | INT | Auto-increment primary key | Yes |
| `property_id` | VARCHAR(100) | Unique property identifier | Yes |
| `title` | VARCHAR(500) | Short property description | No |
| `long_description` | TEXT | Detailed property description | Yes |
| `location` | VARCHAR(255) | Full address | Yes |
| `city` | VARCHAR(100) | City name | No |
| `state` | VARCHAR(100) | State/Province | No |
| `zipcode` | VARCHAR(20) | Postal code | No |
| `price` | DECIMAL(15,2) | Property price | Yes |
| `bedrooms` | INT | Number of bedrooms | No |
| `bathrooms` | DECIMAL(3,1) | Number of bathrooms | No |
| `square_feet` | INT | Property size in sq ft | No |
| `lot_size` | DECIMAL(10,2) | Lot size in acres | No |
| `year_built` | INT | Construction year | No |
| `property_type` | VARCHAR(100) | Type (house, apartment, etc.) | No |
| `listing_date` | DATE | When property was listed | No |
| `status` | VARCHAR(50) | Active, Sold, Pending, etc. | Yes |
| `agent_name` | VARCHAR(255) | Listing agent name | No |
| `agent_contact` | VARCHAR(100) | Agent contact info | No |
| `inspection_report_url` | TEXT | URL to inspection report | No |
| `certificate_url` | TEXT | URL to certificates | No |
| `created_at` | TIMESTAMP | Record creation time | Auto |
| `updated_at` | TIMESTAMP | Last update time | Auto |


