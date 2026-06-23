from pathlib import Path
from datetime import datetime


class RulesManager:
    """Manages rules and direction files inside a workspace."""

    def __init__(self, workspace_path: Path):
        self.rules_dir = workspace_path / "rules"
        self.rules_dir.mkdir(parents=True, exist_ok=True)

    def list_rules(self) -> list[str]:
        return sorted(
            [f.name for f in self.rules_dir.iterdir() if f.suffix == ".md"]
        )

    def read_rule(self, filename: str) -> dict:
        path = self.rules_dir / filename
        if not path.exists():
            return {"error": f"Rule '{filename}' not found."}
        return {
            "filename": filename,
            "content": path.read_text(encoding="utf-8"),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }

    def write_rule(self, filename: str, content: str) -> dict:
        if not filename.endswith(".md"):
            filename += ".md"
        path = self.rules_dir / filename
        path.write_text(content, encoding="utf-8")
        return {"message": f"Rule '{filename}' saved.", "filename": filename}

    def create_rule(self, filename: str) -> dict:
        if not filename.endswith(".md"):
            filename += ".md"
        path = self.rules_dir / filename
        if path.exists():
            return {"error": f"Rule '{filename}' already exists."}
        path.write_text(
            f"# {filename.replace('.md', '')}\n\n## Rules\n\n- Rule 1\n",
            encoding="utf-8",
        )
        return {"message": f"Rule '{filename}' created.", "filename": filename}

    def delete_rule(self, filename: str) -> dict:
        path = self.rules_dir / filename
        if not path.exists():
            return {"error": f"Rule '{filename}' not found."}
        path.unlink()
        return {"message": f"Rule '{filename}' deleted."}

    def get_all_rules_text(self) -> str:
        """Concatenate all rules into a single text block for prompt injection."""
        parts = []
        for name in self.list_rules():
            doc = self.read_rule(name)
            if "content" in doc:
                parts.append(doc["content"])
        return "\n\n---\n\n".join(parts) if parts else ""
