"""
RAG Agent - Retrieval Augmented Generation for semantic search
"""
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import config
import logging

class RAGAgent:
    """Agent for semantic search using embeddings"""
    
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.client = self.connect_qdrant()
        
    def connect_qdrant(self):
        """Connect to Qdrant"""
        try:
            if config.QDRANT_URL and config.QDRANT_API_KEY:
                client = QdrantClient(
                    url=config.QDRANT_URL,
                    api_key=config.QDRANT_API_KEY,
                )
            else:
                client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
            return client
        except Exception as e:
            logging.error(f"Error connecting to Qdrant: {e}")
            return None
    
    def semantic_search(self, query, limit=5, filters=None):
        """
        Perform semantic search using embeddings
        query: user's search query
        limit: number of results to return
        filters: optional filters for metadata
        """
        if not self.client:
            return []
        
        try:
            # Generate embedding for query
            query_vector = self.model.encode(query).tolist()
            
            # Build filter if provided
            search_filter = None
            if filters:
                # Example: filter by price range, city, etc.
                conditions = []
                if 'min_price' in filters:
                    conditions.append({
                        "key": "price",
                        "range": {"gte": filters['min_price']}
                    })
                if 'max_price' in filters:
                    conditions.append({
                        "key": "price",
                        "range": {"lte": filters['max_price']}
                    })
                if 'city' in filters:
                    conditions.append({
                        "key": "city",
                        "match": {"value": filters['city']}
                    })
                
                if conditions:
                    search_filter = {"must": conditions}
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=config.QDRANT_COLLECTION,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
            
            # Format results
            formatted_results = []
            for idx, result in enumerate(results):
                formatted_result = {
                    'property_id': result.payload.get('property_id'),
                    'title': result.payload.get('title'),
                    'description': result.payload.get('description'),
                    'location': result.payload.get('location'),
                    'city': result.payload.get('city'),
                    'price': result.payload.get('price'),
                    'bedrooms': result.payload.get('bedrooms'),
                    'property_type': result.payload.get('property_type'),
                    'similarity_score': result.score,
                    # ADD CITATION
                    'citation': f"[Source: Vector DB | Property ID: {result.payload.get('property_id')} | Relevance: {result.score:.1%}]"
                }
                formatted_results.append(formatted_result)
            # formatted_results = []
            # for result in results:
            #     formatted_results.append({
            #         'property_id': result.payload.get('property_id'),
            #         'title': result.payload.get('title'),
            #         'description': result.payload.get('description'),
            #         'location': result.payload.get('location'),
            #         'city': result.payload.get('city'),
            #         'price': result.payload.get('price'),
            #         'bedrooms': result.payload.get('bedrooms'),
            #         'property_type': result.payload.get('property_type'),
            #         'similarity_score': result.score
            #     })
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            return []
    
    def get_similar_properties(self, property_id, limit=5):
        """Find properties similar to a given property"""
        if not self.client:
            return []
        
        try:
            # Get the property's vector from Qdrant
            results = self.client.scroll(
                collection_name=config.QDRANT_COLLECTION,
                scroll_filter={
                    "must": [
                        {
                            "key": "property_id",
                            "match": {"value": property_id}
                        }
                    ]
                },
                limit=1
            )
            
            if not results[0]:
                return []
            
            # Use the vector to find similar properties
            vector = results[0][0].vector
            similar = self.client.search(
                collection_name=config.QDRANT_COLLECTION,
                query_vector=vector,
                limit=limit + 1  # +1 because the property itself will be in results
            )
            
            # Filter out the original property
            formatted_results = []
            for result in similar:
                if result.payload.get('property_id') != property_id:
                    formatted_results.append({
                        'property_id': result.payload.get('property_id'),
                        'title': result.payload.get('title'),
                        'location': result.payload.get('location'),
                        'price': result.payload.get('price'),
                        'similarity_score': result.score
                    })
            
            return formatted_results[:limit]
            
        except Exception as e:
            logging.error(f"Error finding similar properties: {e}")
            return []
