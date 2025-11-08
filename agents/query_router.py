"""
Query Router - Routes user queries to appropriate agents
"""
import re

class QueryRouter:
    """Routes user queries to the appropriate agent based on intent"""
    
    def __init__(self):
        # Define intents and their keywords
        self.intent_patterns = {
            'search_properties': [
                'find', 'search', 'looking for', 'show me', 'properties', 
                'houses', 'apartments', 'homes', 'bhk'
            ],
            'web_research': [
                'research', 'market', 'market rates', 'market data', 
                'neighborhood', 'area info', 'compare locations'
            ],
            'generate_report': [
                'generate report', 'create report', 'make report', 'download report',
                'pdf report', 'export report', 'report on', 'summary report'
            ],
            'get_statistics': [
                'statistics', 'stats', 'how many', 'total', 'average price',
                'distribution', 'overview'
            ],
            'estimate_renovation': [
                'renovation', 'remodel', 'renovation cost', 'estimate', 
                'how much to renovate', 'renovation price'
            ],
            'save_property': [
                'save', 'favorite', 'bookmark', 'remember this'
            ],
            'view_saved': [
                'saved properties', 'my favorites', 'show saved', 'bookmarks'
            ],
            'similar_properties': [
                'similar', 'like this', 'comparable', 'alternatives'
            ],
            'help': [
                'help', 'what can you do', 'commands', 'how to use'
            ],
            'clear_memory': [
                'clear memory', 'reset', 'forget', 'clear history'
            ]
        }
    
    def route_query(self, user_query):
        """
        Analyze user query and return intent + extracted parameters
        Returns: dict with 'intent' and 'params'
        """
        user_query_lower = user_query.lower()
        
        # Extract numeric values (for price, bedrooms, etc.)
        numbers = re.findall(r'\d+', user_query)
        
        # Detect intent
        intent = self._detect_intent(user_query_lower)
        
        # Extract parameters based on intent
        params = self._extract_parameters(user_query_lower, numbers, intent)
        
        return {
            'intent': intent,
            'params': params,
            'original_query': user_query
        }
    
    def _detect_intent(self, query):
        """Detect the intent from the query"""
        max_matches = 0
        detected_intent = 'search_properties'  # default intent
        
        for intent, keywords in self.intent_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in query)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        return detected_intent
    
    def _extract_parameters(self, query, numbers, intent):
        """Extract parameters from the query"""
        params = {}
        
        # Extract price range
        if 'under' in query or 'below' in query or 'less than' in query:
            if numbers:
                params['max_price'] = int(numbers[0]) * 1000 if int(numbers[0]) < 1000 else int(numbers[0])
        
        if 'above' in query or 'over' in query or 'more than' in query:
            if numbers:
                params['min_price'] = int(numbers[0]) * 1000 if int(numbers[0]) < 1000 else int(numbers[0])
        
        # Extract bedroom count (BHK format or "bedroom")
        bhk_match = re.search(r'(\d+)\s*bhk', query)
        if bhk_match:
            params['bedrooms'] = int(bhk_match.group(1))
        elif 'bedroom' in query:
            bedroom_nums = [int(n) for n in numbers if int(n) <= 10]
            if bedroom_nums:
                params['bedrooms'] = bedroom_nums[0]
        
        # Extract city/location
        cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune', 
                 'kolkata', 'ahmedabad', 'jaipur', 'lucknow', 'gurgaon', 'noida']
        for city in cities:
            if city in query:
                params['city'] = city.title()
                break
        
        # Extract location keywords
        if 'in ' in query:
            location_match = re.search(r'in ([a-z\s]+)', query)
            if location_match and 'city' not in params:
                params['location'] = location_match.group(1).strip()
        
        # Extract property type
        if 'apartment' in query or 'flat' in query:
            params['property_type'] = 'apartment'
        elif 'villa' in query:
            params['property_type'] = 'villa'
        elif 'house' in query:
            params['property_type'] = 'house'
        
        # For renovation estimates
        if intent == 'estimate_renovation':
            sqft_match = re.search(r'(\d+)\s*(sq\.?\s*ft|square\s*feet|sqft)', query)
            if sqft_match:
                params['square_feet'] = int(sqft_match.group(1))
            elif numbers:
                params['square_feet'] = int(numbers[0])
            
            # Renovation type
            if 'luxury' in query:
                params['renovation_type'] = 'luxury'
            elif 'high end' in query or 'premium' in query:
                params['renovation_type'] = 'high_end'
            elif 'basic' in query:
                params['renovation_type'] = 'basic'
            else:
                params['renovation_type'] = 'moderate'
        
        return params
    
    def get_intent_description(self, intent):
        """Get description of what an intent does"""
        descriptions = {
            'search_properties': 'Search for properties based on your criteria',
            'get_statistics': 'Get overview and statistics about available properties',
            'estimate_renovation': 'Estimate renovation costs for a property',
            'save_property': 'Save a property to your favorites',
            'view_saved': 'View your saved/favorited properties',
            'similar_properties': 'Find properties similar to a given one',
            'help': 'Show available commands and help',
            'clear_memory': 'Clear your search history and preferences'
        }
        return descriptions.get(intent, 'Unknown intent')
