"""
Web Research Agent - Fetches external market data
"""

class WebResearchAgent:
    """Agent for market research and neighborhood information"""
    
    def __init__(self):
        # Standard price per sqft for major cities (INR)
        self.city_prices = {
            'mumbai': 25000, 'bangalore': 8000, 'delhi': 12000,
            'hyderabad': 6000, 'pune': 7000, 'chennai': 7500,
            'kolkata': 5000, 'ahmedabad': 4500
        }
    
    # can have api call like Tavily
    # from tavily import TavilyClient

    # class WebResearchAgent:
    #     def __init__(self):
    #         self.tavily = TavilyClient(api_key="api_key")
        
    #     def research_market_rates(self, location):
    #         results = self.tavily.search(f"real estate market rates {location}")
    #         # Parse results...
    def research_market_rates(self, location):
        """Get market rates for a location"""
        location_lower = location.lower()
        
        # Find matching city
        price_per_sqft = 5000  # Default
        for city, price in self.city_prices.items():
            if city in location_lower:
                price_per_sqft = price
                break
        
        return {
            'location': location,
            'avg_price_per_sqft': price_per_sqft,
            'market_trend': 'Stable',
            'growth_rate': 8.5,
            'demand_level': 'Moderate',
            'insights': [
                f"{location} shows steady demand",
                "Good infrastructure development",
                "Expected moderate appreciation"
            ]
        }
    
    def research_neighborhood(self, location):
        """Get neighborhood information"""
        return {
            'location': location,
            'safety_score': 7.5,
            'amenities': ['Shopping malls', 'Hospitals', 'Schools', 'Parks'],
            'transport': 'Metro and bus connectivity available',
            'overall_rating': 8.0
        }
    
    def compare_locations(self, location1, location2):
        """Compare two locations"""
        data1 = self.research_market_rates(location1)
        data2 = self.research_market_rates(location2)
        
        cheaper = location1 if data1['avg_price_per_sqft'] < data2['avg_price_per_sqft'] else location2
        better_growth = location1 if data1['growth_rate'] > data2['growth_rate'] else location2
        
        return {
            'location1': location1,
            'location2': location2,
            'cheaper_location': cheaper,
            'better_growth': better_growth,
            'price1': data1['avg_price_per_sqft'],
            'price2': data2['avg_price_per_sqft'],
            'recommendation': f"{better_growth} offers better investment potential"
        }
    
    def get_property_insights(self, property_data):
        """Analyze if property is fairly priced"""
        location = property_data.get('location', 'Unknown')
        price = property_data.get('price', 0)
        sqft = property_data.get('square_feet', 1000)
        
        market_data = self.research_market_rates(location)
        expected_price = market_data['avg_price_per_sqft'] * sqft
        
        price_diff = ((price - expected_price) / expected_price) * 100
        
        if price_diff < -10:
            verdict = "Good Deal - Below Market Rate"
        elif price_diff < 10:
            verdict = "Fair Price"
        else:
            verdict = "Above Market Rate"
        
        return {
            'expected_price': expected_price,
            'actual_price': price,
            'difference_percent': round(price_diff, 2),
            'verdict': verdict,
            'recommendation': "Consider purchasing" if price_diff < 0 else "Negotiate price"
        }




