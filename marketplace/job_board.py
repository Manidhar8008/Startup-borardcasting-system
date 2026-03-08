from typing import Dict, Any

class JobBoard:
    """
    Marketplace engine for matching brands with creators/agencies.
    """
    def __init__(self, db_session=None):
        self.db = db_session
        self.jobs = []
        
    def post_job(self, brand_id: int, title: str, budget: float, required_skills: list) -> Dict[str, Any]:
        job_id = len(self.jobs) + 1
        job = {
            "id": job_id,
            "brand_id": brand_id,
            "title": title,
            "budget": budget,
            "skills": required_skills,
            "status": "open"
        }
        self.jobs.append(job)
        return {"status": "success", "job_id": job_id}
        
    def list_open_jobs(self):
        return [j for j in self.jobs if j["status"] == "open"]
