from config import Config

class ProspectScorer:
    """Score prospects based on quality and fit"""
    
    def __init__(self):
        self.config = Config()
    
    def calculate_score(self, prospect_data):
        """Calculate prospect quality score (0-100)"""
        score = 0
        
        # Contact completeness (25 points)
        score += self._score_contact_info(prospect_data)
        
        # Project clarity (25 points)
        score += self._score_project_clarity(prospect_data)
        
        # Budget (25 points)
        score += self._score_budget(prospect_data)
        
        # Urgency (25 points)
        score += self._score_urgency(prospect_data)
        
        return min(100, score)  # Cap at 100
    
    def _score_contact_info(self, prospect):
        """Score based on contact information"""
        score = 0
        
        if prospect.get('email'):
            score += 12
        if prospect.get('phone'):
            score += 8
        if prospect.get('website'):
            score += 5
        
        return min(25, score)
    
    def _score_project_clarity(self, prospect):
        """Score based on project description clarity"""
        score = 0
        
        if prospect.get('project_type'):
            score += 10
        
        desc = prospect.get('project_description', '')
        if desc:
            if len(desc) > 200:
                score += 12
            elif len(desc) > 50:
                score += 8
            else:
                score += 3
        
        return min(25, score)
    
    def _score_budget(self, prospect):
        """Score based on budget information"""
        score = 0
        
        if prospect.get('budget_mentioned'):
            score += 15
        
        budget = prospect.get('budget_estimate', 0)
        if budget >= self.config.MIN_BUDGET:
            score += 10
        
        return min(25, score)
    
    def _score_urgency(self, prospect):
        """Score based on urgency signals"""
        urgency = prospect.get('urgency', 'low')
        
        if urgency == 'high':
            return 25
        elif urgency == 'medium':
            return 15
        return 5
