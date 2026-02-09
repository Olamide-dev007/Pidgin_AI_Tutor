"""
Simple analytics tracker for visa evidence
"""
import json
import os
from datetime import datetime

class Analytics:
    def __init__(self, filepath="data/analytics.json"):
        self.filepath = filepath
        os.makedirs("data", exist_ok=True)
        
        # Load existing data
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "total_sessions": 0,
                "total_messages": 0,
                "total_feedback": 0,
                "topics": {"math": 0, "coding": 0, "general": 0},
                "daily_users": {},
                "started": datetime.now().isoformat()
            }
    
    def log_session(self):
        """Log a new user session"""
        self.data["total_sessions"] += 1
        today = datetime.now().strftime("%Y-%m-%d")
        self.data["daily_users"][today] = self.data["daily_users"].get(today, 0) + 1
        self.save()
    
    def log_message(self, topic="general"):
        """Log a message"""
        self.data["total_messages"] += 1
        self.data["topics"][topic] = self.data["topics"].get(topic, 0) + 1
        self.save()
    
    def log_feedback(self):
        """Log feedback given"""
        self.data["total_feedback"] += 1
        self.save()
    
    def save(self):
        """Save analytics data"""
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_stats(self):
        """Get current statistics"""
        return self.data