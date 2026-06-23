import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACES_DIR = Path(__file__).resolve().parent.parent / "workspaces"

SDD_TEMPLATES = {
    "SPEC": """# Specification — {project_name}

## Overview
Describe the project purpose and high-level goals.

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Constraints
- Technical constraints
- Business constraints

## User Stories
As a [role], I want [feature] so that [benefit].

## Acceptance Criteria
- Criterion 1
- Criterion 2

## Non-Functional Requirements
- Performance
- Security
- Scalability
""",
    "PLAN": """# Plan — {project_name}

## Architecture
High-level architecture description.

## Data Model
| Entity   | Fields              | Relationships |
|----------|---------------------|---------------|
| Example  | id, name, ...       | has_many ...  |

## Implementation Steps
1. Step one
2. Step two
3. Step three

## Tech Stack
- Backend:
- Frontend:
- Database:

## Milestones
| Milestone | Status      | Target Date |
|-----------|-------------|-------------|
| MVP       | In Progress | 2024-01-01  |
""",
    "TASK": """# Tasks — {project_name}

## Backlog
- [ ] Task 1: Description
- [ ] Task 2: Description

## In Progress
- [ ] Task 3: Description

## Done
- [x] Task 4: Description

## Task Details

### Task 1
**Priority:** High
**Estimated effort:** 2h
**Description:**
**Steps:**
1.
2.
3.
**Definition of Done:**
- [ ]
""",
}


class SDDManager:
    """Manages SDD artifacts (SPEC.md, PLAN.md, TASK.md) inside workspaces."""

    def __init__(self):
        WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

    # ── Workspace CRUD ──────────────────────────────────────────────

    def list_workspaces(self) -> list[str]:
        if not WORKSPACES_DIR.exists():
            return []
        return sorted(
            [
                d.name
                for d in WORKSPACES_DIR.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
        )

    @staticmethod
    def _validate_name(name: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))

    def create_workspace(self, name: str, description: str = "") -> dict:
        if not self._validate_name(name):
            return {"error": "Invalid workspace name. Use only letters, numbers, hyphens, and underscores."}
        ws = WORKSPACES_DIR / name
        if ws.exists():
            return {"error": f"Workspace '{name}' already exists."}
        ws.mkdir(parents=True)
        sdd_dir = ws / "sdd"
        sdd_dir.mkdir()
        rules_dir = ws / "rules"
        rules_dir.mkdir()
        memory_dir = ws / "memory"
        memory_dir.mkdir()

        # Write default metadata
        meta = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        (ws / "workspace.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Create SDD templates
        for doc_type, template in SDD_TEMPLATES.items():
            (sdd_dir / f"{doc_type}.md").write_text(
                template.format(project_name=name), encoding="utf-8"
            )

        # Default rules file
        (rules_dir / "DEFAULT_RULES.md").write_text(
            "# Default Rules\n\n"
            "## Code Style\n"
            "- Follow PEP 8 for Python.\n"
            "- Use type hints.\n\n"
            "## Architecture\n"
            "- Separate concerns.\n"
            "- Keep functions small and focused.\n\n"
            "## AI Interaction\n"
            "- Always reference SPEC.md before generating code.\n"
            "- Generate one task at a time from TASK.md.\n"
            "- Validate output against PLAN.md architecture.\n",
            encoding="utf-8",
        )

        return {"workspace": name, "message": f"Workspace '{name}' created."}

    def delete_workspace(self, name: str) -> dict:
        import shutil
        if not self._validate_name(name):
            return {"error": "Invalid workspace name."}
        ws = WORKSPACES_DIR / name
        if not ws.exists():
            return {"error": f"Workspace '{name}' not found."}
        shutil.rmtree(ws)
        return {"message": f"Workspace '{name}' deleted."}

    def get_workspace_meta(self, name: str) -> dict:
        if not self._validate_name(name):
            return {"error": "Invalid workspace name."}
        ws = WORKSPACES_DIR / name
        meta_path = ws / "workspace.json"
        if not meta_path.exists():
            return {"error": "Workspace not found."}
        return json.loads(meta_path.read_text(encoding="utf-8"))

    # ── SDD Document CRUD ───────────────────────────────────────────

    def list_documents(self, workspace: str) -> list[str]:
        if not self._validate_name(workspace):
            return []
        sdd_dir = WORKSPACES_DIR / workspace / "sdd"
        if not sdd_dir.exists():
            return []
        return sorted([f.name for f in sdd_dir.iterdir() if f.suffix == ".md"])

    def _safe_path(self, workspace: str, subfolder: str, filename: str) -> Path | None:
        base = (WORKSPACES_DIR / workspace / subfolder).resolve()
        target = (base / filename).resolve()
        if not str(target).startswith(str(base)):
            return None
        return target

    def read_document(self, workspace: str, filename: str) -> dict:
        path = self._safe_path(workspace, "sdd", filename)
        if path is None:
            return {"error": f"Invalid filename '{filename}'."}
        if not path.exists():
            return {"error": f"'{filename}' not found in workspace '{workspace}'."}
        return {
            "filename": filename,
            "content": path.read_text(encoding="utf-8"),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }

    def write_document(self, workspace: str, filename: str, content: str) -> dict:
        path = self._safe_path(workspace, "sdd", filename)
        if path is None:
            return {"error": f"Invalid filename '{filename}'."}
        if not path.parent.exists():
            return {"error": f"Workspace '{workspace}' not found."}
        path.write_text(content, encoding="utf-8")
        return {"message": f"'{filename}' saved.", "filename": filename}

    def create_document(self, workspace: str, filename: str) -> dict:
        if not filename.endswith(".md"):
            filename += ".md"
        path = self._safe_path(workspace, "sdd", filename)
        if path is None:
            return {"error": f"Invalid filename '{filename}'."}
        if not path.parent.exists():
            return {"error": f"Workspace '{workspace}' not found."}
        if path.exists():
            return {"error": f"'{filename}' already exists."}
        path.write_text(f"# {filename.replace('.md', '')}\n\n", encoding="utf-8")
        return {"message": f"'{filename}' created.", "filename": filename}

    def delete_document(self, workspace: str, filename: str) -> dict:
        path = self._safe_path(workspace, "sdd", filename)
        if path is None:
            return {"error": f"Invalid filename '{filename}'."}
        if not path.exists():
            return {"error": f"'{filename}' not found."}
        path.unlink()
        return {"message": f"'{filename}' deleted."}

    def get_sdd_context(self, workspace: str) -> str:
        """Build a combined SDD context string for prompt injection."""
        parts = []
        for doc_type in ["SPEC", "PLAN", "TASK"]:
            doc = self.read_document(workspace, f"{doc_type}.md")
            if "content" in doc:
                parts.append(f"=== {doc_type}.md ===\n{doc['content']}")
        return "\n\n".join(parts)
