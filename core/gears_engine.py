"""
GEARS — Goals · Examples · Actions · Rules · Style

A structured prompt-engineering framework that ensures AI interactions
are consistent, high-quality, and aligned with project requirements.
"""

from dataclasses import dataclass, field, asdict, fields
from pathlib import Path
import json
from datetime import datetime

GEARS_SECTIONS = ["goals", "examples", "actions", "rules", "style"]

GEARS_TEMPLATE = {
    "goals": "Define what the AI should accomplish in this interaction.",
    "examples": "Provide concrete examples of expected input/output.",
    "actions": "List the specific steps the AI must take.",
    "rules": "Hard constraints the AI must never violate.",
    "style": "Tone, format, and presentation guidelines.",
}


@dataclass
class GearsProfile:
    """A GEARS profile captures structured prompt-engineering directives."""

    name: str
    goals: str = ""
    examples: str = ""
    actions: str = ""
    rules: str = ""
    style: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def to_prompt_block(self) -> str:
        """Render the profile as a structured prompt block for system injection."""
        lines = ["## GEARS Profile\n"]
        for section in GEARS_SECTIONS:
            value = getattr(self, section)
            if value.strip():
                lines.append(f"### {section.capitalize()}")
                lines.append(value.strip())
                lines.append("")
        return "\n".join(lines)


class GearsEngine:
    """Manages GEARS profiles stored as JSON files inside a workspace."""

    def __init__(self, workspace_path: Path):
        self.profiles_dir = workspace_path / "gears"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    # ── CRUD ────────────────────────────────────────────────────────

    def list_profiles(self) -> list[str]:
        return sorted(
            [
                f.stem
                for f in self.profiles_dir.iterdir()
                if f.suffix == ".json"
            ]
        )

    def get_profile(self, name: str) -> GearsProfile | None:
        path = self.profiles_dir / f"{name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        # Filter to only known fields to prevent crashes on unknown keys
        known = {f.name for f in fields(GearsProfile)}
        return GearsProfile(**{k: v for k, v in data.items() if k in known})

    def save_profile(self, profile: GearsProfile) -> dict:
        profile.updated_at = datetime.now().isoformat()
        path = self.profiles_dir / f"{profile.name}.json"
        path.write_text(
            json.dumps(profile.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {"message": f"Profile '{profile.name}' saved."}

    def delete_profile(self, name: str) -> dict:
        path = self.profiles_dir / f"{name}.json"
        if not path.exists():
            return {"error": f"Profile '{name}' not found."}
        path.unlink()
        return {"message": f"Profile '{name}' deleted."}

    # ── Prompt Assembly ─────────────────────────────────────────────

    def build_system_prompt(
        self,
        profile_name: str,
        sdd_context: str = "",
        rules_text: str = "",
    ) -> str:
        """Assemble a full system prompt from GEARS + SDD + Rules."""
        parts: list[str] = []

        profile = self.get_profile(profile_name)
        if profile:
            parts.append(profile.to_prompt_block())

        if sdd_context.strip():
            parts.append(f"## Project SDD Context\n\n{sdd_context}")

        if rules_text.strip():
            parts.append(f"## Rules & Constraints\n\n{rules_text}")

        if not parts:
            return (
                "You are an expert AI coding assistant. "
                "Help the user with their software development tasks."
            )

        header = (
            "You are an expert AI coding assistant operating within a "
            "Specification-Driven Development (SDD) workflow.\n"
            "Follow the structured directives below carefully.\n\n"
        )
        return header + "\n---\n\n".join(parts)


# ── Default profiles ───────────────────────────────────────────────

DEFAULT_PROFILES = {
    "code_generator": GearsProfile(
        name="code_generator",
        goals=(
            "Generate clean, production-ready code that follows the "
            "project architecture defined in PLAN.md and satisfies "
            "requirements in SPEC.md."
        ),
        examples=(
            "**Input:** 'Implement the user registration endpoint'\n"
            "**Output:** A complete Flask route with validation, error "
            "handling, and response formatting."
        ),
        actions=(
            "1. Read the relevant SPEC.md and PLAN.md sections.\n"
            "2. Identify the exact task from TASK.md.\n"
            "3. Generate code that matches the architecture.\n"
            "4. Include error handling and input validation.\n"
            "5. Add inline comments for complex logic."
        ),
        rules=(
            "- Never generate code outside the scope of SPEC.md.\n"
            "- Always use the patterns from PLAN.md.\n"
            "- Do not hardcode secrets or credentials.\n"
            "- Include type hints for Python code."
        ),
        style=(
            "- Use concise, readable code.\n"
            "- Follow PEP 8 for Python.\n"
            "- Use descriptive variable names."
        ),
    ),
    "task_planner": GearsProfile(
        name="task_planner",
        goals=(
            "Break down PLAN.md implementation steps into atomic, "
            "testable tasks for TASK.md."
        ),
        examples=(
            "**Input:** PLAN.md step 'Implement authentication'\n"
            "**Output:** 4-5 granular tasks covering login, logout, "
            "token management, etc."
        ),
        actions=(
            "1. Read PLAN.md and SPEC.md.\n"
            "2. Identify the next unimplemented step.\n"
            "3. Break it into small, estimable tasks.\n"
            "4. Each task should be completable in 1-4 hours.\n"
            "5. Update TASK.md with the new tasks."
        ),
        rules=(
            "- Each task must have a clear definition of done.\n"
            "- Tasks must be ordered by dependency.\n"
            "- Include estimated effort for each task."
        ),
        style=(
            "- Use checkbox format: `- [ ] Task description`\n"
            "- Group tasks by phase/milestone."
        ),
    ),
    "code_reviewer": GearsProfile(
        name="code_reviewer",
        goals=(
            "Review generated or existing code against SPEC.md "
            "requirements and PLAN.md architecture."
        ),
        examples=(
            "**Input:** A code diff\n"
            "**Output:** Structured review with issues, suggestions, "
            "and approval status."
        ),
        actions=(
            "1. Compare code against SPEC.md requirements.\n"
            "2. Check architectural compliance with PLAN.md.\n"
            "3. Identify bugs, security issues, and anti-patterns.\n"
            "4. Suggest improvements.\n"
            "5. Provide a pass/fail verdict."
        ),
        rules=(
            "- Be specific about line numbers and issues.\n"
            "- Severity: Critical / Warning / Suggestion.\n"
            "- Never approve code that violates SPEC.md."
        ),
        style=(
            "- Use structured markdown for review output.\n"
            "- Group issues by severity."
        ),
    ),
}
