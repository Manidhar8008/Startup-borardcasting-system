class AgencyProfile:
    """
    Profile management for entire Marketing Agencies on the platform.
    """
    def __init__(self, db_session=None):
        self.db = db_session
        
    def get_agency(self, agency_id: int):
        return {
            "id": agency_id,
            "name": "GrowthX Media",
            "specialties": ["B2B SaaS", "Founder Branding"],
            "minimum_retainer": 5000,
            "team_size": 12,
            "certified_partner": True
        }
