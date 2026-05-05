import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib.parse import urljoin, urlparse

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, redirect, session, url_for, flash, g
from data.auth import authenticate_user, create_or_get_oauth_user, create_user, get_user_by_id
from data.chat import (
    init_chat_db,
    create_chat_session,
    add_chat_message,
    get_chat_sessions,
    get_chat_messages,
    delete_chat_session,
    update_session_timestamp
)
from data.memory import new_session_id, save_message, search_memories
from data.questions import get_topics
from data.progress import clear_progress, load_progress, mark_visited, question_key, update_progress
from data.teacher import TeacherAgent

# Initialize databases
init_chat_db()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-for-production")

if os.environ.get("FLASK_ENV") != "production":
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


@app.before_request
def load_current_user():
    g.current_user = get_current_user()


@app.context_processor
def inject_current_user():
    return {"current_user": g.get("current_user")}


def current_user_id():
    return g.current_user["id"] if g.get("current_user") else 0


@app.template_filter('email_preview')
def email_preview(email):
    if not email:
        return ''
    return email if len(email) <= 20 else email[:18] + '…'


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def send_signup_confirmation(email: str) -> dict:
    subject = "Welcome to ReetCode"
    body = (
        f"Hi there,\n\n"
        f"Thanks for joining ReetCode with {email}. Your account has been created successfully.\n\n"
        "Master data structures and algorithms through interactive problem-solving. Build skills for technical interviews, coding practice, or pure problem-solving growth.\n\n"
        "If you have any questions, just hit reply to this message.\n\n"
        "Happy coding,\n"
        "The ReetCode Team\n"
    )

    # Send email via SMTP
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_server, smtp_username, smtp_password]):
        app.logger.warning("SMTP not configured, logging email instead")
        app.logger.info("Signup confirmation email for %s:\nSubject: %s\n\n%s", email, subject, body)
        return {"subject": subject, "body": body}

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        app.logger.info("Signup confirmation email sent to %s", email)
    except Exception as e:
        app.logger.error("Failed to send email to %s: %s", email, str(e))
        # Fallback to logging
        app.logger.info("Signup confirmation email for %s:\nSubject: %s\n\n%s", email, subject, body)

    return {"subject": subject, "body": body}


def _topics_with_progress(user_id: int = 0):
    topics = get_topics()
    progress = load_progress(user_id=user_id)
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
    topics = _topics_with_progress(user_id=current_user_id())
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
    return render_template("index.html", topics=_topics_with_progress(user_id=current_user_id()))

@app.route("/topic/<topic_slug>")
def topic(topic_slug):
    topics = _topics_with_progress(user_id=current_user_id())
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    if not topic_data:
        return "Topic not found", 404
    return render_template("topic.html", topic=topic_data, all_topics=topics)

@app.route("/question/<topic_slug>/<int:q_index>")
def question(topic_slug, q_index):
    if not g.current_user:
        return redirect(url_for("login", next=request.path))

    topics = get_topics()
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    if not topic_data or q_index >= len(topic_data["questions"]):
        return "Not found", 404
    progress_key = question_key(topic_slug, topic_data["questions"][q_index], q_index)
    mark_visited(progress_key, user_id=current_user_id())
    topics = _topics_with_progress(user_id=current_user_id())
    topic_data = next((t for t in topics if t["slug"] == topic_slug), None)
    q = topic_data["questions"][q_index]
    return render_template("question.html", question=q, topic=topic_data, q_index=q_index, all_topics=topics)

@app.route("/api/topics")
def api_topics():
    return jsonify(_topics_with_progress(user_id=current_user_id()))

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
        user_id=current_user_id(),
    )
    return jsonify({"ok": True, "progress": entry})


@app.route("/completed")
def completed():
    if not g.current_user:
        return redirect(url_for("login", next=request.path))
    topics = _topics_with_progress(user_id=current_user_id())
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
    if not g.current_user:
        return redirect(url_for("login", next=request.path))
    topics = _topics_with_progress(user_id=current_user_id())
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


@app.route("/login/google")
def login_google():
    next_page = request.args.get("next")
    if next_page and is_safe_url(next_page):
        session["next_url"] = next_page
    return oauth.google.authorize_redirect(url_for("auth_google", _external=True))


@app.route("/auth/google")
def auth_google():
    token = oauth.google.authorize_access_token()
    if not token:
        flash("Google authentication failed.", "error")
        return redirect(url_for("login"))

    user_info = token.get("userinfo")
    if not user_info:
        try:
            user_info = oauth.google.parse_id_token(token)
        except Exception:
            user_info = None

    if not user_info or not user_info.get("email"):
        flash("Unable to retrieve an email address from Google.", "error")
        return redirect(url_for("login"))

    user = create_or_get_oauth_user(user_info["email"], "google")
    if not user:
        flash("Unable to sign in with Google.", "error")
        return redirect(url_for("login"))

    session["user_id"] = user["id"]
    session["session_id"] = new_session_id()
    next_page = session.pop("next_url", None)
    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    flash("Signed in with Google.", "success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next")
    if request.method == "POST":
        next_page = request.form.get("next") or next_page
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = authenticate_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["session_id"] = new_session_id()
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("login.html", next=next_page)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    next_page = request.args.get("next")
    if request.method == "POST":
        next_page = request.form.get("next") or next_page
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""
        if not email or not password:
            flash("Please provide both email and password.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            user = create_user(email, password)
            if user is None:
                flash("Email already in use. Try logging in.", "error")
            else:
                send_signup_confirmation(user["email"])
                session["user_id"] = user["id"]
                session["session_id"] = new_session_id()
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                flash("Account created successfully. A confirmation email has been sent.", "success")
                return redirect(url_for("index"))
    return render_template("signup.html", next=next_page)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/reset-progress")
def reset_progress():
    if not g.current_user:
        return redirect(url_for("login", next=request.path))

    clear_progress(current_user_id())
    flash("All progress has been reset. You can start fresh now.", "success")
    return redirect(request.referrer or url_for("index"))


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


# Practice Mode Chat API Routes
@app.route("/api/chat/start", methods=["POST"])
def start_chat_session():
    """Start a new chat session with selected topics"""
    if not g.current_user:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json()
    selected_topics = data.get("topics", [])
    session_name = data.get("session_name", f"Learning Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    if not selected_topics:
        return jsonify({"error": "At least one topic must be selected"}), 400

    session_id = create_chat_session(current_user_id(), session_name, selected_topics)

    # Initialize teacher agent
    teacher = TeacherAgent(session_id, selected_topics)
    initial_message = teacher.generate_response("")

    # Save teacher's initial message
    add_chat_message(session_id, "teacher", initial_message)

    return jsonify({
        "ok": True,
        "session_id": session_id,
        "initial_message": initial_message
    })


@app.route("/api/chat/<int:session_id>/message", methods=["POST"])
def send_chat_message(session_id):
    """Send a message in a chat session"""
    if not g.current_user:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Verify session belongs to user
    sessions = get_chat_sessions(current_user_id())
    session_ids = [s['id'] for s in sessions]
    if session_id not in session_ids:
        return jsonify({"error": "Session not found"}), 404

    # Get session details
    session = next(s for s in sessions if s['id'] == session_id)
    selected_topics = session['selected_topics']

    # Save user message
    add_chat_message(session_id, "student", user_message)

    # Generate teacher response
    teacher = TeacherAgent(session_id, selected_topics)
    teacher_response = teacher.generate_response(user_message)

    # Save teacher response
    add_chat_message(session_id, "teacher", teacher_response)

    # Update session timestamp
    update_session_timestamp(session_id)

    return jsonify({
        "ok": True,
        "response": teacher_response
    })


@app.route("/api/chat/<int:session_id>", methods=["GET"])
def get_chat_session(session_id):
    """Get chat session details and messages"""
    if not g.current_user:
        return jsonify({"error": "Authentication required"}), 401

    # Verify session belongs to user
    sessions = get_chat_sessions(current_user_id())
    session = next((s for s in sessions if s['id'] == session_id), None)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    messages = get_chat_messages(session_id)

    return jsonify({
        "ok": True,
        "session": session,
        "messages": messages
    })


@app.route("/api/chat/<int:session_id>", methods=["DELETE"])
def delete_chat_session_route(session_id):
    """Delete a chat session"""
    if not g.current_user:
        return jsonify({"error": "Authentication required"}), 401

    success = delete_chat_session(session_id, current_user_id())
    if not success:
        return jsonify({"error": "Session not found or access denied"}), 404

    return jsonify({"ok": True})


@app.route("/practice")
def practice():
    if not g.current_user:
        return redirect(url_for("login", next=request.path))

    # Get user's chat sessions for history
    chat_sessions = get_chat_sessions(current_user_id())
    topics = _topics_with_progress(user_id=current_user_id())

    return render_template(
        "practice.html",
        topics=topics,
        chat_sessions=chat_sessions,
        page='practice'
    )

@app.route("/live-interview")
def live_interview():
    return render_template("live_interview.html", topics=_topics_with_progress(), page='live-interview')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
