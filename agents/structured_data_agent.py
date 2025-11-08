"""
Structured Data Agent - Queries MySQL database for property data
"""
from sqlalchemy import create_engine, text
import pandas as pd
import config
import logging

class StructuredDataAgent:
    """Agent for querying structured property data from MySQL"""
    
    def __init__(self):
        self.engine = self.create_engine()
        
    def create_engine(self):
        """Create SQLAlchemy engine"""
        connection_string = (
            f"mysql+mysqlconnector://{config.MYSQL_CONFIG['user']}:"
            f"{config.MYSQL_CONFIG['password']}@{config.MYSQL_CONFIG['host']}:"
            f"{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']}"
        )
        return create_engine(connection_string)
    
    def search_properties(self, filters=None):
        """
        Search properties with filters
        Only uses columns that actually exist: property_id, long_description, location, price, listing_date, status
        """
        query = "SELECT * FROM properties WHERE 1=1"
        params = {}
        
        if filters:
            # Price filters - WORKS (price column exists)
            if 'min_price' in filters and filters['min_price']:
                query += " AND price >= :min_price"
                params['min_price'] = filters['min_price']
            
            if 'max_price' in filters and filters['max_price']:
                query += " AND price <= :max_price"
                params['max_price'] = filters['max_price']
            
            # Location/city filter - WORKS (location column exists)
            if 'city' in filters and filters['city']:
                query += " AND location LIKE :city"
                params['city'] = f"%{filters['city']}%"
            
            if 'location' in filters and filters['location']:
                query += " AND location LIKE :location"
                params['location'] = f"%{filters['location']}%"
            
        
        query += " LIMIT 50"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                columns = result.keys()
                data = []
                for row in result.fetchall():
                    row_dict = dict(zip(columns, row))
                    # Map to expected format for UI
                    mapped = {
                        'property_id': row_dict.get('property_id', ''),
                        'title': row_dict.get('long_description', '')[:100] + '...',  # Use description as title
                        'long_description': row_dict.get('long_description', ''),
                        'location': row_dict.get('location', ''),
                        'city': row_dict.get('location', ''),  # Use location as city
                        'price': float(row_dict.get('price', 0)),
                        'bedrooms': 0,  # Not available
                        'bathrooms': 0,  # Not available
                        'square_feet': 0,  # Not available
                        'property_type': 'N/A',  # Not available
                        'status': row_dict.get('status', 'Active'),
                        'listing_date': row_dict.get('listing_date')
                    }
                    data.append(mapped)
                return data
        except Exception as e:
            logging.error(f"Error searching properties: {e}")
            return []
    
    def get_property_by_id(self, property_id):
        """Get a single property by ID"""
        query = "SELECT * FROM properties WHERE property_id = :property_id"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'property_id': property_id})
                row = result.fetchone()
                if row:
                    columns = result.keys()
                    row_dict = dict(zip(columns, row))
                    return {
                        'property_id': row_dict.get('property_id', ''),
                        'title': row_dict.get('long_description', '')[:100],
                        'long_description': row_dict.get('long_description', ''),
                        'location': row_dict.get('location', ''),
                        'price': float(row_dict.get('price', 0)),
                        'status': row_dict.get('status', 'Active')
                    }
                return None
        except Exception as e:
            logging.error(f"Error getting property: {e}")
            return None
    
    def get_statistics(self):
        """Get database statistics"""
        stats = {}
        try:
            with self.engine.connect() as conn:
                # Total properties
                result = conn.execute(text("SELECT COUNT(*) FROM properties"))
                stats['total_properties'] = result.fetchone()[0]
                
                # Average price
                result = conn.execute(text("SELECT AVG(price) FROM properties WHERE price > 0"))
                stats['avg_price'] = result.fetchone()[0] or 0
                
                # Min price
                result = conn.execute(text("SELECT MIN(price) FROM properties WHERE price > 0"))
                stats['min_price'] = result.fetchone()[0] or 0
                
                # Max price
                result = conn.execute(text("SELECT MAX(price) FROM properties WHERE price > 0"))
                stats['max_price'] = result.fetchone()[0] or 0
                
                # Distinct locations (as "cities")
                result = conn.execute(text("SELECT DISTINCT location FROM properties WHERE location != '' LIMIT 10"))
                stats['cities'] = [row[0] for row in result.fetchall()]
            
            return stats
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {}
    
    def get_price_distribution(self):
        """Get price distribution for visualization"""
        query = """
        SELECT 
            CASE 
                WHEN price < 1000 THEN 'Under 1K'
                WHEN price < 2000 THEN '1K-2K'
                WHEN price < 3000 THEN '2K-3K'
                WHEN price < 5000 THEN '3K-5K'
                ELSE '5K+'
            END as price_range,
            COUNT(*) as count
        FROM properties
        WHERE price > 0
        GROUP BY price_range
        ORDER BY 
            CASE 
                WHEN price < 1000 THEN 1
                WHEN price < 2000 THEN 2
                WHEN price < 3000 THEN 3
                WHEN price < 5000 THEN 4
                ELSE 5
            END
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                data = [{'range': row[0], 'count': row[1]} for row in result.fetchall()]
                return data
        except Exception as e:
            logging.error(f"Error getting price distribution: {e}")
            return []




# """
# Structured Data Agent - Queries MySQL database for property data
# """
# from sqlalchemy import create_engine, text
# import pandas as pd
# import config
# import logging

# class StructuredDataAgent:
#     """Agent for querying structured property data from MySQL"""
    
#     def __init__(self):
#         self.engine = self.create_engine()
        
#     def create_engine(self):
#         """Create SQLAlchemy engine"""
#         connection_string = (
#             f"mysql+mysqlconnector://{config.MYSQL_CONFIG['user']}:"
#             f"{config.MYSQL_CONFIG['password']}@{config.MYSQL_CONFIG['host']}:"
#             f"{config.MYSQL_CONFIG['port']}/{config.MYSQL_CONFIG['database']}"
#         )
#         return create_engine(connection_string)
    
#     def search_properties(self, filters=None):
#         """
#         Search properties with filters
#         filters: dict with keys like 'min_price', 'max_price', 'city', 'bedrooms', etc.
#         """
#         query = "SELECT * FROM properties WHERE 1=1"
#         params = {}
        
#         if filters:
#             if 'min_price' in filters and filters['min_price']:
#                 query += " AND price >= :min_price"
#                 params['min_price'] = filters['min_price']
            
#             if 'max_price' in filters and filters['max_price']:
#                 query += " AND price <= :max_price"
#                 params['max_price'] = filters['max_price']
            
#             if 'city' in filters and filters['city']:
#                 query += " AND location LIKE :city" 
#                 params['city'] = f"%{filters['city']}%"
            
#             if 'bedrooms' in filters and filters['bedrooms']:
#                 query += " AND num_rooms >= :num_rooms"
#                 params['num_rooms'] = filters['bedrooms']
            
#             if 'property_type' in filters and filters['property_type']:
#                 query += " AND property_type LIKE :property_type"
#                 params['property_type'] = f"%{filters['property_type']}%"
            
#             if 'location' in filters and filters['location']:
#                 query += " AND location LIKE :location"
#                 params['location'] = f"%{filters['location']}%"
        
#         query += " LIMIT 50"
        
#         try:
#             with self.engine.connect() as conn:
#                 result = conn.execute(text(query), params)
#                 columns = result.keys()
#                 data = [dict(zip(columns, row)) for row in result.fetchall()]
#                 return data
#         except Exception as e:
#             logging.error(f"Error searching properties: {e}")
#             return []
    
#     def get_property_by_id(self, property_id):
#         """Get a single property by ID"""
#         query = "SELECT * FROM properties WHERE property_id = :property_id"
        
#         try:
#             with self.engine.connect() as conn:
#                 result = conn.execute(text(query), {'property_id': property_id})
#                 row = result.fetchone()
#                 if row:
#                     columns = result.keys()
#                     return dict(zip(columns, row))
#                 return None
#         except Exception as e:
#             logging.error(f"Error getting property: {e}")
#             return None
    
#     def get_statistics(self):
#         """Get database statistics"""
#         queries = {
#             'total_properties': "SELECT COUNT(*) as count FROM properties",
#             'avg_price': "SELECT AVG(price) as avg_price FROM properties WHERE price > 0",
#             'min_price': "SELECT MIN(price) as min_price FROM properties WHERE price > 0",
#             'max_price': "SELECT MAX(price) as max_price FROM properties WHERE price > 0"
#             # 'cities': "SELECT DISTINCT city FROM properties WHERE location != '' LIMIT 10"
#         }
        
#         stats = {}
#         try:
#             with self.engine.connect() as conn:
#                 for key, query in queries.items():
#                     result = conn.execute(text(query))
#                     if key == 'cities':
#                         stats[key] = [row[0] for row in result.fetchall()]
#                     else:
#                         row = result.fetchone()
#                         stats[key] = row[0] if row else 0
#             return stats
#         except Exception as e:
#             logging.error(f"Error getting statistics: {e}")
#             return {}
    
#     def get_price_distribution(self):
#         """Get price distribution for visualization"""
#         query = """
#         SELECT 
#             CASE 
#                 WHEN price < 50000 THEN '0-50K'
#                 WHEN price < 100000 THEN '50-100K'
#                 WHEN price < 200000 THEN '100-200K'
#                 WHEN price < 500000 THEN '200-500K'
#                 ELSE '500K+'
#             END as price_range,
#             COUNT(*) as count
#         FROM properties
#         WHERE price > 0
#         GROUP BY price_range
#         ORDER BY 
#             CASE 
#                 WHEN price < 50000 THEN 1
#                 WHEN price < 100000 THEN 2
#                 WHEN price < 200000 THEN 3
#                 WHEN price < 500000 THEN 4
#                 ELSE 5
#             END
#         """
        
#         try:
#             with self.engine.connect() as conn:
#                 result = conn.execute(text(query))
#                 data = [{'range': row[0], 'count': row[1]} for row in result.fetchall()]
#                 return data
#         except Exception as e:
#             logging.error(f"Error getting price distribution: {e}")
#             return []
