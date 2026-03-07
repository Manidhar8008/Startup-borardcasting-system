"""File-based approval queue for brand content."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATABASES_DIR = ROOT / "databases"


class ApprovalQueue:
    def __init__(self, brand: str):
        self.brand = brand
        self.brand_dir = DATABASES_DIR / brand
        self.brand_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_file("ideas.json", [])
        self._ensure_file("approved.json", [])
        self._ensure_file("drafts.json", [])
        self._ensure_file("published.json", [])
        self._ensure_file("rejected.json", [])

    def _ensure_file(self, name: str, default):
        path = self.brand_dir / name
        if not path.exists():
            with path.open("w", encoding="utf-8") as f:
                json.dump(default, f)

    def _load(self, name: str) -> List[Dict]:
        path = self.brand_dir / name
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, name: str, data: List[Dict]):
        path = self.brand_dir / name
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # Ideas -------------------------------------------------
    def add_idea(self, idea: Dict) -> Dict:
        ideas = self._load("ideas.json")
        item = {
            **idea,
            "id": idea.get("id") or f"idea-{len(ideas)+1}",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        ideas.append(item)
        self._write("ideas.json", ideas)
        return item

    def list_ideas(self, status: Optional[str] = None) -> List[Dict]:
        ideas = self._load("ideas.json")
        if status:
            ideas = [i for i in ideas if i.get("status") == status]
        return ideas

    def set_idea_status(self, idea_id: str, status: str, reason: str | None = None) -> Optional[Dict]:
        ideas = self._load("ideas.json")
        approved = self._load("approved.json")
        updated = None
        for idea in ideas:
            if idea.get("id") == idea_id:
                idea["status"] = status
                if reason:
                    idea["reason"] = reason
                idea["updated_at"] = datetime.utcnow().isoformat() + "Z"
                updated = idea
                break
        if updated:
            self._write("ideas.json", ideas)
            if status == "approved":
                if not any(i.get("id") == idea_id for i in approved):
                    approved.append(updated)
                self._write("approved.json", approved)
            else:
                filtered = [i for i in approved if i.get("id") != idea_id]
                self._write("approved.json", filtered)
        return updated

    def list_approved(self) -> List[Dict]:
        return self._load("approved.json")

    # Drafts ------------------------------------------------
    def add_draft(self, draft: Dict) -> Dict:
        drafts = self._load("drafts.json")
        item = {
            **draft,
            "id": draft.get("id") or f"draft-{len(drafts)+1}",
            "status": "draft",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        drafts.append(item)
        self._write("drafts.json", drafts)
        return item

    def list_drafts(self) -> List[Dict]:
        return self._load("drafts.json")

    # Publishing --------------------------------------------
    def publish(self, draft_id: str) -> Optional[Dict]:
        drafts = self._load("drafts.json")
        published = self._load("published.json")
        remaining = []
        published_item = None
        for d in drafts:
            if d.get("id") == draft_id:
                published_item = {
                    **d,
                    "status": "published",
                    "published_at": datetime.utcnow().isoformat() + "Z",
                }
                published.append(published_item)
            else:
                remaining.append(d)
        if published_item:
            self._write("drafts.json", remaining)
            self._write("published.json", published)
        return published_item

    def reject_draft(self, draft_id: str, reason: str) -> Optional[Dict]:
        drafts = self._load("drafts.json")
        rejected = self._load("rejected.json")
        remaining = []
        rejected_item = None
        for d in drafts:
            if d.get("id") == draft_id:
                rejected_item = {
                    **d,
                    "status": "rejected",
                    "rejected_at": datetime.utcnow().isoformat() + "Z",
                    "reason": reason,
                }
                rejected.append(rejected_item)
            else:
                remaining.append(d)
        if rejected_item:
            self._write("drafts.json", remaining)
            self._write("rejected.json", rejected)
        return rejected_item

    def list_published(self) -> List[Dict]:
        return self._load("published.json")

    def list_rejected(self) -> List[Dict]:
        return self._load("rejected.json")


if __name__ == "__main__":
    queue = ApprovalQueue("janani_ai")
    idea = queue.add_idea({"topic": "Test", "summary": "Sample"})
    queue.set_idea_status(idea["id"], "approved")
