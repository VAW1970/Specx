from pathlib import Path
from .sdd_manager import SDDManager
from .gears_engine import GearsEngine
from .rules_manager import RulesManager
from .memory_bank import MemoryBank

WORKSPACES_DIR = Path(__file__).resolve().parent.parent / "workspaces"


class PromptBuilder:
    """Assembles a complete system prompt from all available context sources.

    Sources (in order of priority):
      1. GEARS profile directives
      2. SDD documents (SPEC, PLAN, TASK)
      3. Rules & directions files
      4. Memory bank context
    """

    def __init__(self, workspace: str):
        self.workspace = workspace
        self.ws_path = WORKSPACES_DIR / workspace
        self.sdd = SDDManager()
        self.gears = GearsEngine(self.ws_path)
        self.rules = RulesManager(self.ws_path)
        self.memory = MemoryBank(self.ws_path)

    def build_full_prompt(
        self,
        gears_profile: str | None = None,
        include_sdd: bool = True,
        include_rules: bool = True,
        include_memory: bool = True,
        custom_instructions: str = "",
    ) -> str:
        parts: list[str] = []

        # Header
        parts.append(
            "# Specx AI Assistant\n"
            "You are an expert software development assistant operating "
            "within a Specification-Driven Development (SDD) workflow.\n"
        )

        # 1. GEARS profile
        if gears_profile:
            profile = self.gears.get_profile(gears_profile)
            if profile:
                parts.append(profile.to_prompt_block())

        # 2. SDD context
        if include_sdd:
            sdd_ctx = self.sdd.get_sdd_context(self.workspace)
            if sdd_ctx.strip():
                parts.append(f"## Project SDD Context\n\n{sdd_ctx}")

        # 3. Rules
        if include_rules:
            rules_text = self.rules.get_all_rules_text()
            if rules_text.strip():
                parts.append(f"## Rules & Constraints\n\n{rules_text}")

        # 4. Memory
        if include_memory:
            mem_ctx = self.memory.build_memory_context()
            if mem_ctx.strip():
                parts.append(f"## Project Memory\n\n{mem_ctx}")

        # 5. Custom instructions
        if custom_instructions.strip():
            parts.append(f"## Additional Instructions\n\n{custom_instructions}")

        return "\n\n---\n\n".join(parts)
