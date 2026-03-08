class CreatorProfile:
    """
    Profile management for freelance content creators operating on the JAN AI network.
    """
    def __init__(self, db_session=None):
        self.db = db_session
        
    def get_creator(self, creator_id: int):
        # Mock database fetch
        return {
            "id": creator_id,
            "name": "Alex Mercer",
            "skills": ["Short-form Video", "LinkedIn Ghostwriting"],
            "rating": 4.9,
            "hourly_rate": 150,
            "verified": True
        }
        
    def search_creators(self, skill: str, max_rate: int):
        # Mock search
        creators = [self.get_creator(1)]
        return [c for c in creators if skill in c["skills"] and c["hourly_rate"] <= max_rate]
