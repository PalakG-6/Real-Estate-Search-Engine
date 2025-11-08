"""
Task Planner Agent - Decomposes complex queries into ordered subtasks
"""
import re
from typing import List, Dict

class TaskPlannerAgent:
    """Agent for breaking down complex queries into executable tasks"""
    
    def __init__(self):
        self.task_templates = {
            'search_and_estimate': [
                {'action': 'search_properties', 'description': 'Find matching properties'},
                {'action': 'estimate_renovation', 'description': 'Calculate renovation costs'},
                {'action': 'generate_summary', 'description': 'Create summary'}
            ],
            'search_and_report': [
                {'action': 'search_properties', 'description': 'Find matching properties'},
                {'action': 'analyze_results', 'description': 'Analyze property data'},
                {'action': 'generate_report', 'description': 'Create PDF report'}
            ],
            'compare_and_recommend': [
                {'action': 'search_properties', 'description': 'Find properties in location A'},
                {'action': 'search_properties', 'description': 'Find properties in location B'},
                {'action': 'compare_results', 'description': 'Compare properties'},
                {'action': 'generate_recommendation', 'description': 'Recommend best option'}
            ],
            'research_and_search': [
                {'action': 'web_research', 'description': 'Research market rates'},
                {'action': 'search_properties', 'description': 'Find matching properties'},
                {'action': 'compare_with_market', 'description': 'Compare with market data'}
            ]
        }
    
    def analyze_query_complexity(self, query: str) -> Dict:
        """
        Analyze if query is complex and needs task decomposition
        Returns: {'is_complex': bool, 'complexity_score': int, 'reasons': []}
        """
        complexity_indicators = {
            'multiple_actions': ['and then', 'after that', 'also', 'plus', 'additionally'],
            'comparison': ['compare', 'versus', 'vs', 'better', 'difference between'],
            'multi_step': ['find', 'estimate', 'generate', 'create', 'analyze'],
            'conditional': ['if', 'depending on', 'based on'],
            'multiple_locations': []  # Will detect multiple location names
        }
        
        query_lower = query.lower()
        complexity_score = 0
        reasons = []
        
        # Check for multiple action verbs
        action_verbs = ['find', 'search', 'estimate', 'calculate', 'generate', 
                       'create', 'compare', 'analyze', 'show', 'get']
        action_count = sum(1 for verb in action_verbs if verb in query_lower)
        if action_count > 1:
            complexity_score += action_count
            reasons.append(f'Multiple actions detected: {action_count}')
        
        # Check for complexity indicators
        for category, keywords in complexity_indicators.items():
            if any(keyword in query_lower for keyword in keywords):
                complexity_score += 2
                reasons.append(f'Contains {category} indicators')
        
        # Check for "and" connections
        and_count = query_lower.count(' and ')
        if and_count > 0:
            complexity_score += and_count
            reasons.append(f'Multiple clauses connected with "and": {and_count}')
        
        is_complex = complexity_score >= 3
        
        return {
            'is_complex': is_complex,
            'complexity_score': complexity_score,
            'reasons': reasons
        }
    
    def decompose_query(self, query: str) -> List[Dict]:
        """
        Break down complex query into ordered subtasks
        Returns: List of task dicts with action, params, and description
        """
        query_lower = query.lower()
        tasks = []
        
        # Pattern 1: "Find X and estimate Y"
        if 'find' in query_lower and 'estimate' in query_lower:
            # Extract search parameters
            search_task = {
                'step': 1,
                'action': 'search_properties',
                'description': 'Search for properties matching criteria',
                'params': self._extract_search_params(query),
                'output': 'property_list'
            }
            tasks.append(search_task)
            
            # Extract estimation parameters
            estimate_task = {
                'step': 2,
                'action': 'estimate_renovation',
                'description': 'Calculate renovation costs for found properties',
                'params': self._extract_renovation_params(query),
                'input': 'property_list',
                'output': 'renovation_estimates'
            }
            tasks.append(estimate_task)
            
            # Check if report is requested
            if any(word in query_lower for word in ['report', 'pdf', 'summary', 'document']):
                report_task = {
                    'step': 3,
                    'action': 'generate_report',
                    'description': 'Generate PDF report with results',
                    'params': {'include_estimates': True},
                    'input': ['property_list', 'renovation_estimates'],
                    'output': 'pdf_report'
                }
                tasks.append(report_task)
        
        # Pattern 2: "Find X, compare with Y, generate report"
        elif 'compare' in query_lower:
            # Extract two sets of search criteria
            parts = re.split(r'\band\b|\bwith\b|\bvs\b|\bversus\b', query_lower)
            
            for i, part in enumerate(parts[:2], 1):
                search_task = {
                    'step': i,
                    'action': 'search_properties',
                    'description': f'Search for properties in criteria set {i}',
                    'params': self._extract_search_params(part),
                    'output': f'property_list_{i}'
                }
                tasks.append(search_task)
            
            compare_task = {
                'step': len(tasks) + 1,
                'action': 'compare_properties',
                'description': 'Compare properties from both searches',
                'params': {},
                'input': [f'property_list_{i}' for i in range(1, min(3, len(parts)+1))],
                'output': 'comparison_results'
            }
            tasks.append(compare_task)
            
            if 'report' in query_lower or 'summary' in query_lower:
                report_task = {
                    'step': len(tasks) + 1,
                    'action': 'generate_report',
                    'description': 'Generate comparison report',
                    'params': {'report_type': 'comparison'},
                    'input': 'comparison_results',
                    'output': 'pdf_report'
                }
                tasks.append(report_task)
        
        # Pattern 3: "Research market in X and find properties"
        elif 'research' in query_lower or 'market' in query_lower:
            research_task = {
                'step': 1,
                'action': 'web_research',
                'description': 'Research market rates and trends',
                'params': self._extract_location(query),
                'output': 'market_data'
            }
            tasks.append(research_task)
            
            search_task = {
                'step': 2,
                'action': 'search_properties',
                'description': 'Search for properties',
                'params': self._extract_search_params(query),
                'output': 'property_list'
            }
            tasks.append(search_task)
            
            analysis_task = {
                'step': 3,
                'action': 'analyze_market_fit',
                'description': 'Compare properties with market data',
                'params': {},
                'input': ['property_list', 'market_data'],
                'output': 'analysis_results'
            }
            tasks.append(analysis_task)
        
        # Pattern 4: Simple multi-step queries
        else:
            # Check for multiple actions
            if 'find' in query_lower or 'search' in query_lower:
                tasks.append({
                    'step': 1,
                    'action': 'search_properties',
                    'description': 'Search for properties',
                    'params': self._extract_search_params(query),
                    'output': 'property_list'
                })
            
            if 'estimate' in query_lower or 'renovation' in query_lower:
                tasks.append({
                    'step': len(tasks) + 1,
                    'action': 'estimate_renovation',
                    'description': 'Estimate renovation costs',
                    'params': self._extract_renovation_params(query),
                    'output': 'renovation_estimate'
                })
            
            if any(word in query_lower for word in ['report', 'pdf', 'summary']):
                tasks.append({
                    'step': len(tasks) + 1,
                    'action': 'generate_report',
                    'description': 'Generate report',
                    'params': {},
                    'output': 'pdf_report'
                })
        
        # If no tasks were created, return a simple search
        if not tasks:
            tasks = [{
                'step': 1,
                'action': 'search_properties',
                'description': 'Process user query',
                'params': self._extract_search_params(query),
                'output': 'results'
            }]
        
        return tasks
    
    def _extract_search_params(self, query: str) -> Dict:
        """Extract search parameters from query text"""
        params = {}
        query_lower = query.lower()
        
        # Extract price
        price_match = re.search(r'under (\d+)', query_lower)
        if price_match:
            params['max_price'] = int(price_match.group(1))
        
        # Extract location
        location = self._extract_location(query)
        if location:
            params['city'] = location
        
        # Extract bedrooms
        bhk_match = re.search(r'(\d+)\s*bhk', query_lower)
        if bhk_match:
            params['bedrooms'] = int(bhk_match.group(1))
        
        return params
    
    def _extract_renovation_params(self, query: str) -> Dict:
        """Extract renovation parameters from query"""
        params = {}
        
        # Extract square feet
        sqft_match = re.search(r'(\d+)\s*(?:sq\.?\s*ft|square\s*feet)', query.lower())
        if sqft_match:
            params['square_feet'] = int(sqft_match.group(1))
        
        # Extract renovation type
        if 'luxury' in query.lower():
            params['renovation_type'] = 'luxury'
        elif 'basic' in query.lower():
            params['renovation_type'] = 'basic'
        else:
            params['renovation_type'] = 'moderate'
        
        return params
    
    def _extract_location(self, query: str) -> str:
        """Extract location from query"""
        common_cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 
                        'pune', 'kolkata', 'ahmedabad', 'jaipur', 'lucknow']
        
        query_lower = query.lower()
        for city in common_cities:
            if city in query_lower:
                return city.title()
        
        # Try to extract after "in"
        in_match = re.search(r'\bin\s+([a-z]+)', query_lower)
        if in_match:
            return in_match.group(1).title()
        
        return None
    
    def create_execution_plan(self, tasks: List[Dict]) -> str:
        """
        Create a human-readable execution plan
        """
        plan = "📋 **Execution Plan:**\n\n"
        
        for task in tasks:
            plan += f"**Step {task['step']}:** {task['description']}\n"
            if task.get('params'):
                plan += f"  - Parameters: {task['params']}\n"
        
        plan += f"\n**Total Steps:** {len(tasks)}"
        
        return plan
