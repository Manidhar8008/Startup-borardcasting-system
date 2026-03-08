class CreatorGraph:
    """
    Maps freelance creators across the marketplace to skills and brands.
    """
    def __init__(self):
        self.creators = {}
        
    def add_creator(self, creator_id: str, skills: list, successful_formats: list):
        self.creators[creator_id] = {
            "skills": skills,
            "best_formats": successful_formats,
            "brand_affinities": {}
        }
        
    def link_to_brand(self, creator_id: str, brand_id: int, engagement_yield: float):
        if creator_id in self.creators:
            self.creators[creator_id]["brand_affinities"][brand_id] = engagement_yield
