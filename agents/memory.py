"""
Memory Component - Stores user preferences and conversation history
"""
import json
import os
from datetime import datetime

class MemoryManager:
    """Manages user memory across sessions"""
    
    def __init__(self, memory_file='data/user_memory.json'):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        
    def load_memory(self):
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            'preferences': {},
            'search_history': [],
            'saved_properties': [],
            'conversation_history': []
        }
    
    def save_memory(self):
        """Save memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def update_preference(self, key, value):
        """Update user preference"""
        self.memory['preferences'][key] = value
        self.save_memory()
    
    def get_preference(self, key, default=None):
        """Get user preference"""
        return self.memory['preferences'].get(key, default)
    
    def add_search(self, query, results_count):
        """Add search to history"""
        search_entry = {
            'query': query,
            'results_count': results_count,
            'timestamp': datetime.now().isoformat()
        }
        self.memory['search_history'].append(search_entry)
        # Keep only last 50 searches
        self.memory['search_history'] = self.memory['search_history'][-50:]
        self.save_memory()
    
    def save_property(self, property_id, property_info):
        """Save a property to favorites"""
        saved = {
            'property_id': property_id,
            'info': property_info,
            'saved_at': datetime.now().isoformat()
        }
        # Check if already saved
        if not any(p['property_id'] == property_id for p in self.memory['saved_properties']):
            self.memory['saved_properties'].append(saved)
            self.save_memory()
            return True
        return False
    
    def get_saved_properties(self):
        """Get all saved properties"""
        return self.memory['saved_properties']
    
    def add_conversation(self, user_message, bot_response):
        """Add conversation turn"""
        conversation = {
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        }
        self.memory['conversation_history'].append(conversation)
        # Keep only last 20 conversations
        self.memory['conversation_history'] = self.memory['conversation_history'][-20:]
        self.save_memory()
    
    def get_conversation_history(self, last_n=5):
        """Get recent conversation history"""
        return self.memory['conversation_history'][-last_n:]
    
    def clear_memory(self):
        """Clear all memory"""
        self.memory = {
            'preferences': {},
            'search_history': [],
            'saved_properties': [],
            'conversation_history': []
        }
        self.save_memory()
