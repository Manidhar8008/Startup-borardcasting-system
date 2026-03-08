import logging
from enum import Enum
from typing import List, Dict

logger = logging.getLogger("team_manager")

class Role(Enum):
    OWNER = "Owner"
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class TeamManager:
    """
    Handles RBAC (Role-Based Access Control) for enterprise brands
    managing multiple team members on the platform.
    """
    def __init__(self, db_session=None):
        self.db = db_session
        self.teams = {}
        
    def add_member(self, brand_id: int, user_email: str, role: Role, invited_by: str) -> Dict[str, str]:
        logger.info(f"Adding {user_email} to brand {brand_id} as {role.value}")
        if brand_id not in self.teams:
            self.teams[brand_id] = []
            
        self.teams[brand_id].append({"email": user_email, "role": role.value})
        return {"status": "success", "message": f"Invited {user_email} as {role.value}."}

    def check_permission(self, brand_id: int, user_email: str, required_role: Role) -> bool:
        """
        Validates if a user has sufficient privileges to perform an action.
        """
        role_hierarchy = {Role.VIEWER: 1, Role.EDITOR: 2, Role.ADMIN: 3, Role.OWNER: 4}
        
        team = self.teams.get(brand_id, [])
        user_record = next((u for u in team if u["email"] == user_email), None)
        
        if not user_record:
            return False
            
        user_role_enum = Role(user_record["role"])
        return role_hierarchy[user_role_enum] >= role_hierarchy[required_role]
