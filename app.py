"""
Specx — Specification-Driven Development with Ollama
Main Flask application.
"""

import json
from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    redirect,
    url_for,
    flash,
    stream_with_context,
)

import re
from functools import wraps
from core.ollama_client import OllamaClient
from core.sdd_manager import SDDManager, WORKSPACES_DIR
from core.gears_engine import GearsEngine, DEFAULT_PROFILES, GEARS_SECTIONS
from core.rules_manager import RulesManager
from core.memory_bank import MemoryBank, MEMORY_TYPES
from core.prompt_builder import PromptBuilder

app = Flask(__name__)
app.secret_key = "specx-dev-secret-key-change-in-production"

# Service instances
ollama = OllamaClient()
sdd = SDDManager()

# ── Helpers ─────────────────────────────────────────────────────────

_WS_NAME_RE = re.compile(r'^[a-zA-Z0-9_-]+$')


def _validate_ws(name: str) -> bool:
    return bool(_WS_NAME_RE.match(name))


def _ws_path(name: str) -> Path:
    return WORKSPACES_DIR / name


def require_valid_ws(f):
    """Decorator to reject workspace names with path traversal."""
    @wraps(f)
    def decorated(*args, **kwargs):
        name = kwargs.get("name", "")
        if not _validate_ws(name):
            flash("Invalid workspace name.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ── Help ───────────────────────────────────────────────────────────


@app.route("/help")
def help_page():
    return render_template("help.html")


# ── Dashboard ───────────────────────────────────────────────────────


@app.route("/")
def index():
    workspaces = sdd.list_workspaces()
    models = ollama.list_models()
    return render_template("index.html", workspaces=workspaces, models=models)


# ── Models ──────────────────────────────────────────────────────────


@app.route("/models")
def models_page():
    models = ollama.list_models()
    return render_template("models.html", models=models)


@app.route("/api/models")
def api_models():
    return jsonify(ollama.list_models())


@app.route("/models/pull", methods=["POST"])
def pull_model():
    model_name = request.form.get("model_name", "")
    if not model_name:
        flash("Model name is required.", "error")
        return redirect(url_for("models_page"))
    result = ollama.pull_model(model_name)
    flash(result, "success" if "successfully" in result else "error")
    return redirect(url_for("models_page"))


# ── Workspace CRUD ──────────────────────────────────────────────────


@app.route("/workspace/new", methods=["POST"])
def workspace_new():
    name = request.form.get("name", "").strip()
    desc = request.form.get("description", "").strip()
    if not name:
        flash("Workspace name is required.", "error")
        return redirect(url_for("index"))
    result = sdd.create_workspace(name, desc)
    if "error" in result:
        flash(result["error"], "error")
    else:
        flash(result["message"], "success")
    return redirect(url_for("index"))


@app.route("/workspace/<name>")
@require_valid_ws
def workspace_detail(name: str):
    meta = sdd.get_workspace_meta(name)
    documents = sdd.list_documents(name)
    gears = GearsEngine(_ws_path(name))
    profiles = gears.list_profiles()
    rules = RulesManager(_ws_path(name))
    rule_files = rules.list_rules()
    memory = MemoryBank(_ws_path(name))
    memory_entries = {mtype: len(memory.list_entries(mtype)) for mtype in MEMORY_TYPES}
    models = ollama.list_models()
    return render_template(
        "workspace.html",
        workspace=name,
        meta=meta,
        documents=documents,
        gear_profiles=profiles,
        rule_files=rule_files,
        memory_entries=memory_entries,
        models=models,
    )


@app.route("/workspace/<name>/delete", methods=["POST"])
@require_valid_ws
def workspace_delete(name: str):
    result = sdd.delete_workspace(name)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("index"))


# ── SDD Editor ──────────────────────────────────────────────────────


@app.route("/workspace/<name>/sdd/<filename>")
@require_valid_ws
def sdd_edit(name: str, filename: str):
    doc = sdd.read_document(name, filename)
    if "error" in doc:
        flash(doc["error"], "error")
        return redirect(url_for("workspace_detail", name=name))
    documents = sdd.list_documents(name)
    return render_template(
        "sdd_editor.html",
        workspace=name,
        filename=filename,
        content=doc.get("content", ""),
        documents=documents,
    )


@app.route("/workspace/<name>/sdd/<filename>/save", methods=["POST"])
@require_valid_ws
def sdd_save(name: str, filename: str):
    content = request.form.get("content", "")
    result = sdd.write_document(name, filename, content)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("sdd_edit", name=name, filename=filename))


@app.route("/workspace/<name>/sdd/new", methods=["POST"])
@require_valid_ws
def sdd_new(name: str):
    filename = request.form.get("filename", "").strip()
    if not filename:
        flash("Filename is required.", "error")
        return redirect(url_for("workspace_detail", name=name))
    result = sdd.create_document(name, filename)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("workspace_detail", name=name))


@app.route("/workspace/<name>/sdd/<filename>/delete", methods=["POST"])
@require_valid_ws
def sdd_delete(name: str, filename: str):
    result = sdd.delete_document(name, filename)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("workspace_detail", name=name))


# ── AI Chat ─────────────────────────────────────────────────────────


@app.route("/workspace/<name>/chat")
@require_valid_ws
def chat_page(name: str):
    models = ollama.list_models()
    gears = GearsEngine(_ws_path(name))
    profiles = gears.list_profiles()
    return render_template(
        "chat.html",
        workspace=name,
        models=models,
        gear_profiles=profiles,
    )


@app.route("/workspace/<name>/chat/send", methods=["POST"])
@require_valid_ws
def chat_send(name: str):
    data = request.get_json()
    user_message = data.get("message", "")
    model = data.get("model", "llama3")
    profile_name = data.get("gears_profile", "")
    include_sdd = data.get("include_sdd", True)
    include_rules = data.get("include_rules", True)
    include_memory = data.get("include_memory", True)

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    # Build system prompt
    builder = PromptBuilder(name)
    system_prompt = builder.build_full_prompt(
        gears_profile=profile_name or None,
        include_sdd=include_sdd,
        include_rules=include_rules,
        include_memory=include_memory,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    def generate():
        try:
            stream = ollama.chat(model=model, messages=messages, stream=True)
            for chunk in stream:
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/workspace/<name>/chat/quick", methods=["POST"])
@require_valid_ws
def chat_quick(name: str):
    """Non-streaming quick chat for simple interactions."""
    data = request.get_json()
    user_message = data.get("message", "")
    model = data.get("model", "llama3")
    profile_name = data.get("gears_profile", "")

    builder = PromptBuilder(name)
    system_prompt = builder.build_full_prompt(gears_profile=profile_name or None)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = ollama.chat(model=model, messages=messages, stream=False)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GEARS Profiles ──────────────────────────────────────────────────


@app.route("/workspace/<name>/gears")
@require_valid_ws
def gears_page(name: str):
    gears = GearsEngine(_ws_path(name))
    profiles = gears.list_profiles()
    profile_data = []
    for p in profiles:
        prof = gears.get_profile(p)
        if prof:
            profile_data.append(prof.to_dict())
    return render_template(
        "gears.html",
        workspace=name,
        profiles=profile_data,
        sections=GEARS_SECTIONS,
        default_profiles=DEFAULT_PROFILES,
    )


@app.route("/workspace/<name>/api/gears")
@require_valid_ws
def api_gears_list(name: str):
    gears = GearsEngine(_ws_path(name))
    profiles = gears.list_profiles()
    profile_data = []
    for p in profiles:
        prof = gears.get_profile(p)
        if prof:
            profile_data.append({"name": prof.name, "description": prof.description})
    return jsonify({"profiles": profile_data})


@app.route("/workspace/<name>/gears/save", methods=["POST"])
@require_valid_ws
def gears_save(name: str):
    gears = GearsEngine(_ws_path(name))
    profile_name = request.form.get("profile_name", "").strip()
    if not profile_name:
        flash("Profile name is required.", "error")
        return redirect(url_for("gears_page", name=name))

    existing = gears.get_profile(profile_name)
    from core.gears_engine import GearsProfile

    profile = GearsProfile(
        name=profile_name,
        goals=request.form.get("goals", ""),
        examples=request.form.get("examples", ""),
        actions=request.form.get("actions", ""),
        rules=request.form.get("rules", ""),
        style=request.form.get("style", ""),
        created_at=existing.created_at if existing else None,
    )
    result = gears.save_profile(profile)
    flash(result["message"], "success")
    return redirect(url_for("gears_page", name=name))


@app.route("/workspace/<name>/gears/load_default", methods=["POST"])
@require_valid_ws
def gears_load_default(name: str):
    gears = GearsEngine(_ws_path(name))
    default_name = request.form.get("default_name", "")
    if default_name in DEFAULT_PROFILES:
        gears.save_profile(DEFAULT_PROFILES[default_name])
        flash(f"Default profile '{default_name}' loaded.", "success")
    return redirect(url_for("gears_page", name=name))


@app.route("/workspace/<name>/gears/delete", methods=["POST"])
@require_valid_ws
def gears_delete(name: str):
    gears = GearsEngine(_ws_path(name))
    profile_name = request.form.get("profile_name", "")
    result = gears.delete_profile(profile_name)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("gears_page", name=name))


# ── Rules ───────────────────────────────────────────────────────────


@app.route("/workspace/<name>/rules")
@require_valid_ws
def rules_page(name: str):
    rules = RulesManager(_ws_path(name))
    rule_files = rules.list_rules()
    rule_data = []
    for f in rule_files:
        doc = rules.read_rule(f)
        if "content" in doc:
            rule_data.append(doc)
    return render_template(
        "rules.html",
        workspace=name,
        rules=rule_data,
    )


@app.route("/workspace/<name>/rules/save", methods=["POST"])
@require_valid_ws
def rules_save(name: str):
    rules = RulesManager(_ws_path(name))
    filename = request.form.get("filename", "").strip()
    content = request.form.get("content", "")
    if not filename:
        flash("Filename is required.", "error")
        return redirect(url_for("rules_page", name=name))
    result = rules.write_rule(filename, content)
    flash(result["message"], "success")
    return redirect(url_for("rules_page", name=name))


@app.route("/workspace/<name>/rules/new", methods=["POST"])
@require_valid_ws
def rules_new(name: str):
    rules = RulesManager(_ws_path(name))
    filename = request.form.get("filename", "").strip()
    if not filename:
        flash("Filename is required.", "error")
        return redirect(url_for("rules_page", name=name))
    result = rules.create_rule(filename)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("rules_page", name=name))


@app.route("/workspace/<name>/rules/delete", methods=["POST"])
@require_valid_ws
def rules_delete(name: str):
    rules = RulesManager(_ws_path(name))
    filename = request.form.get("filename", "")
    result = rules.delete_rule(filename)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("rules_page", name=name))


# ── Memory Banks ────────────────────────────────────────────────────


@app.route("/workspace/<name>/memory")
@require_valid_ws
def memory_page(name: str):
    memory = MemoryBank(_ws_path(name))
    active_type = request.args.get("type", "context")
    entries = memory.list_entries(active_type)
    return render_template(
        "memory.html",
        workspace=name,
        entries=entries,
        memory_types=MEMORY_TYPES,
        active_type=active_type,
    )


@app.route("/workspace/<name>/memory/add", methods=["POST"])
@require_valid_ws
def memory_add(name: str):
    memory = MemoryBank(_ws_path(name))
    mtype = request.form.get("memory_type", "context")
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    tags = request.form.get("tags", "").strip()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    if not title or not content:
        flash("Title and content are required.", "error")
        return redirect(url_for("memory_page", name=name, type=mtype))
    result = memory.add_entry(mtype, title, content, tag_list)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("memory_page", name=name, type=mtype))


@app.route("/workspace/<name>/memory/delete", methods=["POST"])
@require_valid_ws
def memory_delete(name: str):
    memory = MemoryBank(_ws_path(name))
    mtype = request.form.get("memory_type", "context")
    entry_id = request.form.get("entry_id", "")
    result = memory.delete_entry(mtype, entry_id)
    flash(result.get("message", result.get("error", "")), "success" if "message" in result else "error")
    return redirect(url_for("memory_page", name=name, type=mtype))


@app.route("/workspace/<name>/memory/search", methods=["GET"])
@require_valid_ws
def memory_search(name: str):
    memory = MemoryBank(_ws_path(name))
    mtype = request.args.get("type", "context")
    query = request.args.get("q", "")
    if query:
        entries = memory.search_entries(mtype, query)
    else:
        entries = memory.list_entries(mtype)
    return render_template(
        "memory.html",
        workspace=name,
        entries=entries,
        memory_types=MEMORY_TYPES,
        active_type=mtype,
        search_query=query,
    )


# ── API: Generate SDD with AI ──────────────────────────────────────


@app.route("/workspace/<name>/api/generate", methods=["POST"])
@require_valid_ws
def api_generate(name: str):
    """Use AI to generate or refine SDD documents."""
    data = request.get_json()
    doc_type = data.get("doc_type", "TASK")
    model = data.get("model", "llama3")
    profile_name = data.get("gears_profile", "")
    extra_context = data.get("context", "")

    builder = PromptBuilder(name)
    system_prompt = builder.build_full_prompt(
        gears_profile=profile_name or None,
        custom_instructions=extra_context,
    )

    prompt_map = {
        "SPEC": "Based on the project context, generate or refine the SPEC.md specification document. Focus on requirements, constraints, and acceptance criteria.",
        "PLAN": "Based on SPEC.md, generate or refine the PLAN.md architecture and implementation plan. Include data models, tech stack, and milestones.",
        "TASK": "Based on SPEC.md and PLAN.md, generate or refine the TASK.md task list. Break work into atomic, estimable tasks with priorities.",
    }

    user_prompt = prompt_map.get(
        doc_type,
        f"Generate or refine the {doc_type}.md document.",
    )
    if extra_context:
        user_prompt += f"\n\nAdditional context: {extra_context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    def generate():
        try:
            stream = ollama.chat(model=model, messages=messages, stream=True)
            for chunk in stream:
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
