"""
Renovation Estimation Agent - Estimates renovation costs
"""

class RenovationAgent:
    """Agent for estimating renovation costs"""
    
    def __init__(self):
        # Cost per square foot for different renovation types (in USD)
        self.cost_rates = {
            'basic': 25,      # Basic refresh: paint, minor fixes
            'moderate': 75,   # Moderate: new flooring, kitchen update
            'high_end': 150,  # High-end: complete remodel
            'luxury': 250     # Luxury: premium materials, custom work
        }
        
        # Additional costs for specific rooms/areas
        self.room_costs = {
            'kitchen': {'basic': 5000, 'moderate': 15000, 'high_end': 30000, 'luxury': 50000},
            'bathroom': {'basic': 3000, 'moderate': 8000, 'high_end': 15000, 'luxury': 25000},
            'living_room': {'basic': 2000, 'moderate': 5000, 'high_end': 10000, 'luxury': 20000}
        }
    
    def estimate_cost(self, square_feet, renovation_type='moderate', num_bedrooms=0, num_bathrooms=0):
        """
        Estimate renovation cost
        square_feet: property size in square feet
        renovation_type: 'basic', 'moderate', 'high_end', or 'luxury'
        num_bedrooms: number of bedrooms
        num_bathrooms: number of bathrooms
        """
        if renovation_type not in self.cost_rates:
            renovation_type = 'moderate'
        
        # Base cost calculation
        base_cost = square_feet * self.cost_rates[renovation_type]
        
        # Add kitchen cost (assume 1 kitchen)
        kitchen_cost = self.room_costs['kitchen'][renovation_type]
        
        # Add bathroom costs
        bathroom_cost = num_bathrooms * self.room_costs['bathroom'][renovation_type]
        
        # Add bedroom/living area costs
        bedroom_cost = num_bedrooms * self.room_costs['living_room'][renovation_type]
        
        # Total cost
        total_cost = base_cost + kitchen_cost + bathroom_cost + bedroom_cost
        
        # Calculate breakdown
        breakdown = {
            'base_renovation': base_cost,
            'kitchen': kitchen_cost,
            'bathrooms': bathroom_cost,
            'bedrooms': bedroom_cost,
            'total': total_cost
        }
        
        # Add contingency (10-15%)
        contingency = total_cost * 0.15
        final_total = total_cost + contingency
        
        return {
            'renovation_type': renovation_type,
            'square_feet': square_feet,
            'breakdown': breakdown,
            'subtotal': total_cost,
            'contingency': contingency,
            'total_estimate': final_total,
            'cost_per_sqft': self.cost_rates[renovation_type],
            'notes': self._get_renovation_notes(renovation_type)
        }
    
    def _get_renovation_notes(self, renovation_type):
        """Get description for renovation type"""
        notes = {
            'basic': 'Basic renovation includes: fresh paint, minor repairs, cleaning, basic fixtures',
            'moderate': 'Moderate renovation includes: new flooring, updated kitchen appliances, bathroom refresh, lighting upgrades',
            'high_end': 'High-end renovation includes: complete kitchen remodel, luxury bathroom, hardwood floors, custom cabinetry',
            'luxury': 'Luxury renovation includes: premium materials, smart home integration, designer fixtures, custom everything'
        }
        return notes.get(renovation_type, '')
    
    def compare_renovation_types(self, square_feet, num_bedrooms=0, num_bathrooms=0):
        """Compare costs across all renovation types"""
        comparison = {}
        for reno_type in ['basic', 'moderate', 'high_end', 'luxury']:
            comparison[reno_type] = self.estimate_cost(
                square_feet, reno_type, num_bedrooms, num_bathrooms
            )
        return comparison
