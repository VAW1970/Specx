# Specx — Specification-Driven Development with Ollama

Flask application for AI-assisted software development using **SDD (Specification-Driven Development)** with local **Ollama** models and the **GEARS** prompt engineering framework.

---

## Features

- **Ollama Integration** — Connect to your local Ollama instance, list models, pull new ones, and chat with streaming responses
- **SDD Workspace** — Manage structured documentation: `SPEC.md`, `PLAN.md`, `TASK.md` with built-in editor and preview
- **GEARS Framework** — Structured prompt engineering: **G**oals · **E**xamples · **A**ctions · **R**ules · **S**tyle
- **Rules & Directions** — Create and manage project rules files that are injected into AI context
- **Memory Banks** — Persistent memory: context, decisions, lessons, and conversation summaries
- **AI Generation** — Generate SDD documents directly from the editor using AI with full project context

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally (`ollama serve`)

---

## Quick Start

### Windows

Double-click `start.bat` — it will create the virtual environment, install dependencies, and start the server.

### Manual

```bash
cd specx

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running
ollama serve

# Start the app
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Project Structure

```
specx/
├── app.py                    # Flask application (routes)
├── start.bat                 # One-click startup script
├── requirements.txt          # Python dependencies
├── core/
│   ├── __init__.py
│   ├── ollama_client.py      # Ollama API wrapper (caching, timeout)
│   ├── sdd_manager.py        # SPEC/PLAN/TASK file management
│   ├── gears_engine.py       # GEARS prompt engineering framework
│   ├── rules_manager.py      # Rules & directions files
│   ├── memory_bank.py        # Persistent memory banks
│   └── prompt_builder.py     # System prompt assembly
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html            # Dashboard
│   ├── workspace.html        # Workspace overview
│   ├── sdd_editor.html       # SDD document editor
│   ├── chat.html             # AI chat interface
│   ├── models.html           # Ollama model management
│   ├── gears.html            # GEARS profile editor
│   ├── rules.html            # Rules management
│   └── memory.html           # Memory banks
├── static/
│   ├── css/style.css         # Dark theme styles
│   └── js/app.js             # Client-side utilities
└── workspaces/               # Created at runtime (per-workspace SDD, rules, memory, gears)
```

---

## SDD Workflow

Specx follows a three-file documentation structure:

| File | Purpose |
|------|---------|
| **SPEC.md** | What to build — requirements, constraints, user stories, acceptance criteria |
| **PLAN.md** | How to build — architecture, data model, tech stack, milestones |
| **TASK.md** | What to do now — atomic tasks with priorities and estimates |

Each workspace starts with templates for these three files. Edit them in the built-in markdown editor or generate them with AI.

---

## GEARS Framework

GEARS provides structured prompt engineering with five sections:

| Section | Description |
|---------|-------------|
| **Goals** | What the AI should accomplish |
| **Examples** | Concrete input/output examples |
| **Actions** | Step-by-step instructions |
| **Rules** | Hard constraints |
| **Style** | Tone and formatting guidelines |

Three default profiles are included: `code_generator`, `task_planner`, and `code_reviewer`.

---

## How It Works

1. **Create a workspace** — Sets up SDD templates, rules, and memory directories
2. **Edit SPEC/PLAN/TASK** — Define your project specification
3. **Configure GEARS** — Create or load a prompt engineering profile
4. **Chat with AI** — The system automatically injects SDD context, GEARS profile, rules, and memory into every conversation
5. **Generate with AI** — Use the "Generate with IA" button in the SDD editor to create or refine documents

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Save current form |
| `Tab` | Insert indent in SDD editor |
| `Enter` | Send chat message (Shift+Enter for new line) |

---

## Configuration

The app connects to Ollama at `http://localhost:11434` by default. To change this, edit `core/ollama_client.py`:

```python
ollama = OllamaClient(host="http://your-ollama-host:11434")
```

---

## License

MIT
