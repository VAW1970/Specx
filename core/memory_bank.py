import json
from pathlib import Path
from datetime import datetime

MEMORY_TYPES = ["context", "decisions", "lessons", "conversations"]


class MemoryBank:
    """Persistent memory banks that store project context across sessions.

    Memory types:
      - context:     Ongoing project state and key facts.
      - decisions:   Architectural and design decisions with rationale.
      - lessons:     What worked and what didn't.
      - conversations: Summaries of key AI interactions.
    """

    def __init__(self, workspace_path: Path):
        self.memory_dir = workspace_path / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        for mtype in MEMORY_TYPES:
            (self.memory_dir / mtype).mkdir(exist_ok=True)

    # ── Entry CRUD ──────────────────────────────────────────────────

    def list_entries(self, memory_type: str) -> list[dict]:
        mdir = self.memory_dir / memory_type
        if not mdir.exists():
            return []
        entries = []
        for f in sorted(mdir.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_filename"] = f.name
            entries.append(data)
        return entries

    def get_entry(self, memory_type: str, entry_id: str) -> dict | None:
        path = self.memory_dir / memory_type / f"{entry_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def add_entry(
        self, memory_type: str, title: str, content: str, tags: list[str] | None = None
    ) -> dict:
        if memory_type not in MEMORY_TYPES:
            return {"error": f"Invalid memory type: {memory_type}"}
        mdir = self.memory_dir / memory_type
        mdir.mkdir(exist_ok=True)

        entry_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        entry = {
            "id": entry_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
        }
        path = mdir / f"{entry_id}.json"
        path.write_text(
            json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return {"message": f"Entry '{title}' added.", "id": entry_id}

    def update_entry(
        self, memory_type: str, entry_id: str, updates: dict
    ) -> dict:
        path = self.memory_dir / memory_type / f"{entry_id}.json"
        if not path.exists():
            return {"error": f"Entry '{entry_id}' not found."}
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(updates)
        data["updated_at"] = datetime.now().isoformat()
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return {"message": "Entry updated."}

    def delete_entry(self, memory_type: str, entry_id: str) -> dict:
        path = self.memory_dir / memory_type / f"{entry_id}.json"
        if not path.exists():
            return {"error": f"Entry '{entry_id}' not found."}
        path.unlink()
        return {"message": "Entry deleted."}

    def search_entries(self, memory_type: str, query: str) -> list[dict]:
        """Simple text search across all entries of a given type."""
        results = []
        for entry in self.list_entries(memory_type):
            searchable = (
                entry.get("title", "") + " " + entry.get("content", "")
            ).lower()
            if query.lower() in searchable:
                results.append(entry)
        return results

    # ── Prompt Assembly ─────────────────────────────────────────────

    def build_memory_context(self, max_entries: int = 20) -> str:
        """Build a context string from all memory banks for prompt injection."""
        parts: list[str] = []
        for mtype in MEMORY_TYPES:
            entries = self.list_entries(mtype)[-max_entries:]
            if entries:
                lines = [f"### {mtype.capitalize()} Memory"]
                for e in entries:
                    tags = ", ".join(e.get("tags", []))
                    tag_str = f" [{tags}]" if tags else ""
                    lines.append(f"- **{e['title']}**{tag_str}: {e['content'][:200]}")
                parts.append("\n".join(lines))
        return "\n\n".join(parts) if parts else ""
