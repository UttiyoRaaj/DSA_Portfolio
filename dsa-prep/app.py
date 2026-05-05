from flask import Flask, render_template, jsonify, request
from data.memory import new_session_id, save_message, search_memories
from data.questions import get_topics
from data.progress import load_progress, mark_visited, question_key, update_progress

app = Flask(__name__)


def _topics_with_progress():
    topics = get_topics()
    progress = load_progress()
    for topic in topics:
        completed_count = 0
        visited_count = 0
        tricky_count = 0
        for q_index, question in enumerate(topic["questions"]):
            key = question_key(topic["slug"], question, q_index)
            entry = progress.get(key, {})
            question["progress_key"] = key
            question["progress"] = {
                "visited": bool(entry.get("visited")),
                "complete": bool(entry.get("complete")),
                "status": entry.get("status", "Unsolved"),
                "remarks": entry.get("remarks", ""),
                "tricky": bool(entry.get("tricky")),
            }
            if question["progress"]["visited"]:
                visited_count += 1
            if question["progress"]["complete"]:
                completed_count += 1
            if question["progress"]["tricky"]:
                tricky_count += 1
        topic["visited_count"] = visited_count
        topic["completed_count"] = completed_count
        topic["tricky_count"] = tricky_count
    return topics


@app.context_processor
def inject_site_stats():
    topics = _topics_with_progress()
    question_counts = [len(topic["questions"]) for topic in topics]
    return {
        "stats": {
            "total_topics": len(topics),
            "total_questions": sum(question_counts),
            "max_topic_questions": max(question_counts, default=1),
            "visited_questions": sum(topic["visited_count"] for topic in topics),
            "completed_questions": sum(topic["completed_count"] for topic in topics),
            "tricky_questions": sum(topic["tricky_count"] for topic in topics),
        }
    }

@app.route("/")
def index():
    return render_template("index.html", topics=_topics_with_progress())

@app.route("/topic/<topic_slug>")
def topic(topic_slug):
    topics = _topics_with_progress()
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    if not topic_data:
        return "Topic not found", 404
    return render_template("topic.html", topic=topic_data, all_topics=topics)

@app.route("/question/<topic_slug>/<int:q_index>")
def question(topic_slug, q_index):
    topics = get_topics()
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    if not topic_data or q_index >= len(topic_data["questions"]):
        return "Not found", 404
    progress_key = question_key(topic_slug, topic_data["questions"][q_index], q_index)
    mark_visited(progress_key)
    topics = _topics_with_progress()
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    q = topic_data["questions"][q_index]
    return render_template("question.html", question=q, topic=topic_data, q_index=q_index, all_topics=topics)

@app.route("/api/topics")
def api_topics():
    return jsonify(_topics_with_progress())

@app.route("/api/progress/<path:progress_key>", methods=["POST"])
def api_progress(progress_key):
    data = request.get_json(silent=True) or {}
    tricky = data.get("tricky")
    if isinstance(tricky, str):
        tricky = tricky.lower() in ("1", "true", "yes", "on")
    entry = update_progress(
        progress_key,
        status=data.get("status", "Unsolved"),
        remarks=data.get("remarks", ""),
        tricky=bool(tricky),
    )
    return jsonify({"ok": True, "progress": entry})


@app.route("/completed")
def completed():
    topics = _topics_with_progress()
    groups = []
    for topic in topics:
        questions = [
            {
                "topic_slug": topic["slug"],
                "topic_title": topic["title"],
                "topic_color": topic["color"],
                "q_index": idx,
                "title": q["title"],
                "difficulty": q["difficulty"],
                "leetcode_number": q.get("leetcode_number"),
            }
            for idx, q in enumerate(topic["questions"])
            if q["progress"]["complete"]
        ]
        if questions:
            groups.append({"topic": topic, "questions": questions})
    return render_template(
        "list_view.html",
        page="completed",
        title="Completed Questions",
        subtitle="Questions you have marked solved",
        groups=groups,
    )


@app.route("/tricky")
def tricky():
    topics = _topics_with_progress()
    groups = []
    for topic in topics:
        questions = [
            {
                "topic_slug": topic["slug"],
                "topic_title": topic["title"],
                "topic_color": topic["color"],
                "q_index": idx,
                "title": q["title"],
                "difficulty": q["difficulty"],
                "leetcode_number": q.get("leetcode_number"),
            }
            for idx, q in enumerate(topic["questions"])
            if q["progress"]["tricky"]
        ]
        if questions:
            groups.append({"topic": topic, "questions": questions})
    return render_template(
        "list_view.html",
        page="tricky",
        title="Tricky Questions",
        subtitle="Questions you've flagged as tricky",
        groups=groups,
    )


@app.route("/api/session", methods=["POST"])
def api_session():
    return jsonify({"session_id": new_session_id()})


def _teacher_reply(message: str, memories: list[dict], language_hint: str) -> str:
    lowered = message.lower()
    prefix = ""
    if language_hint == "hinglish":
        prefix = "Bilkul, "
    elif language_hint == "bengali_roman":
        prefix = "Bujhlam, "

    if memories:
        memory = memories[0]["content"]
        memory_line = (
            "Tiny memory refresh: last time you had a related thought around "
            f"\"{memory[:120]}\". Let us connect that to this."
        )
    else:
        memory_line = "Let us build this from the ground up, no drama."

    if any(word in lowered for word in ["forget", "forgot", "bhule", "mone", "yaad", "confuse", "confused"]):
        return (
            prefix
            + memory_line
            + "\n\nHint: first name the pattern, then name the state you keep, then say when that state changes. "
            + "Try explaining only those three things."
        )

    if "why" in lowered or "keno" in lowered or "kyu" in lowered or "kya" in lowered:
        return (
            prefix
            + "Great question. The trick is to ask what information would save us from repeating work. "
            + memory_line
            + "\n\nTell me what you think the repeated work is, and I will nudge from there."
        )

    return (
        prefix
        + "Nice, I am with you. "
        + memory_line
        + "\n\nNow say it back casually: what are we tracking, why does it help, and what edge case might break it?"
    )


def _interview_reply(message: str, memories: list[dict]) -> str:
    if memories:
        return (
            "Noted. I see a related prior discussion in your history, but in this interview please reason from first principles. "
            "Now clarify your approach, complexity, and one edge case."
        )
    return "Understood. Please continue with your approach, expected complexity, and edge cases."


@app.route("/api/conversation", methods=["POST"])
def api_conversation():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or new_session_id()
    mode = data.get("mode", "practice")
    content = (data.get("content") or "").strip()
    topic_slug = data.get("topic_slug")
    topic_title = data.get("topic_title")
    q_key = data.get("question_key")
    question_title = data.get("question_title")

    if not content:
        return jsonify({"ok": False, "error": "Message is required"}), 400

    user_memory = save_message(
        session_id=session_id,
        mode=mode,
        role="student" if mode == "practice" else "candidate",
        content=content,
        topic_slug=topic_slug,
        topic_title=topic_title,
        question_key=q_key,
        question_title=question_title,
    )
    memories = search_memories(content, mode=mode, topic_slug=topic_slug)
    if mode == "practice":
        reply = _teacher_reply(content, memories, user_memory["language_hint"])
        assistant_role = "teacher"
    else:
        reply = _interview_reply(content, memories)
        assistant_role = "interviewer"

    save_message(
        session_id=session_id,
        mode=mode,
        role=assistant_role,
        content=reply,
        topic_slug=topic_slug,
        topic_title=topic_title,
        question_key=q_key,
        question_title=question_title,
    )
    return jsonify({
        "ok": True,
        "session_id": session_id,
        "reply": reply,
        "language_hint": user_memory["language_hint"],
        "memories": memories,
    })


@app.route("/practice")
def practice():
    return render_template("practice.html", topics=_topics_with_progress(), page='practice')

@app.route("/live-interview")
def live_interview():
    return render_template("live_interview.html", topics=_topics_with_progress(), page='live-interview')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
