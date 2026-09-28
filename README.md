# ReetCode — DSA Portfolio & Interview Prep Platform

A full-stack Flask application for structured data-structures-and-algorithms practice. Users can browse a local problem bank, record per-account learning progress, use a deterministic teaching chat, and run an LLM-backed mock interview. The question page also includes an interactive, step-by-step visualizer for the three **Two Sum** approaches.

## Portfolio snapshot

| Area | What is implemented |
| --- | --- |
| Content | 150 JSON-backed questions across 16 DSA topics; 26 Easy, 99 Medium, and 25 Hard |
| Learning flow | Topic browsing, question detail pages, approach comparison, examples, constraints, interview Q&A, and Java solutions |
| Progress | Per-user visited/solved/tricky status and free-form remarks, persisted in SQLite |
| Authentication | Password signup/login with Werkzeug hashes, Google OAuth through Authlib, and Flask sessions |
| AI experiences | Local rule-based teacher chat with persistent sessions; OpenAI- or Cohere-compatible mock interviewer with tool calling |
| Visualization | Modal player for Two Sum brute force, sorted two pointers, and one-pass HashMap; custom input, playback, seek, speed controls, code-line highlighting, and a keyboard-adjustable split pane |

## Problem the project solves

Preparing for DSA interviews often means juggling a spreadsheet of problems, reference solutions, notes, and a separate AI chat. ReetCode brings those workflows together: a curated local problem bank gives predictable content, persistent progress makes study state visible, and the teacher/interviewer modes let a learner switch between explanation and realistic questioning.

## Architecture

```text
Browser (Jinja templates + vanilla JavaScript)
        │
        ├── Page routes / JSON APIs ──> Flask app (app.py)
        │                                  │
        │                                  ├── Question loader ──> question_data/**/*.json
        │                                  ├── Auth, progress, teaching chat ──> SQLite
        │                                  ├── Interview memory ──> conversations SQLite DB
        │                                  └── InterviewAgent ──> OpenAI or Cohere HTTP API
        │
        └── Visualization player <── trace data / client-side trace generator
```

The application uses server-rendered Jinja pages for the main experience, then adds small `fetch`-based interactions where a full page refresh would be unnecessary (saving progress and chatting). This keeps the architecture intentionally simple while still making the UI responsive.

## Core features and how they work

### 1. Data-driven question bank

- Each problem lives in `data/question_data/<topic>/<problem>.json` rather than in Python source.
- A question contains its ID, LeetCode reference, title, difficulty, prompt, examples, constraints, intuition, one or more approaches, code, and interview Q&A.
- `data/questions.py` discovers files, loads them with UTF-8 JSON parsing, sorts them by numeric ID, and attaches topic metadata such as title, color, and icon.
- Adding a problem is primarily a content operation: create a JSON record following the existing schema. Adding a topic also requires an entry in `TOPICS_META`.

Why this is a good design choice: content is separated from application logic, which makes the bank easier to extend and review. The trade-off is that there is no admin UI or schema validation pipeline yet; malformed JSON is discovered at runtime.

### 2. Personalized progress

Opening an authenticated question marks it visited. The question page can save one of two statuses (`Solved` or `Unsolved`), a `tricky` flag, and notes.

- `progress` uses a composite primary key of `(progress_key, user_id)`, so the same question is independently tracked for each learner.
- `progress_key` is a stable, readable value built from topic, question index, and normalized title.
- SQLite `INSERT ... ON CONFLICT ... DO UPDATE` performs an upsert, avoiding a separate read-then-write branch and reducing race windows.
- Topic cards and the completed/tricky pages are calculated from persisted progress at request time.

### 3. Authentication and sessions

- Passwords are never stored directly; `generate_password_hash` and `check_password_hash` from Werkzeug are used.
- Password and Google OAuth identities share a `users` table with an `auth_method` and optional provider field.
- Google OAuth uses OpenID Connect discovery through Authlib. Login redirects are checked with `is_safe_url` to prevent open redirects.
- Flask’s signed session holds the user ID and an in-memory interview session UUID. A confirmation email is sent through SMTP when configured; otherwise the app logs the intended message locally.

### 4. Two learning conversations

The app deliberately separates two different experiences:

| Mode | Implementation | Purpose |
| --- | --- | --- |
| Teacher chat | `TeacherAgent` plus `chat_sessions` / `chat_messages` | Gives deterministic concept explanations, analogy-first responses, topic selection, and lesson continuity without requiring an external model key. |
| Live interview | `InterviewAgent` plus `conversations.db` | Simulates a senior DSA interviewer, retains the most recent conversation context, evaluates approaches/code, and calls an external LLM provider. |

This separation is an important product decision: teaching and interviewing have different desired behaviours. A tutor can explain freely; an interviewer should ask focused follow-ups and reveal solutions gradually.

### 5. Provider-agnostic LLM interviewer

`LLMConfig.from_env()` selects OpenAI by default or Cohere when `LLM_PROVIDER=cohere`. The configuration also supports custom base URL, model, API key fallback, temperature, and a 45-second timeout.

- The system prompt constrains the model to interviewer behaviour: clarification, graduated hints, trade-off discussion, code review, and concise feedback.
- Before every call, the backend supplies the selected problem and a compact summary of the local bank.
- The model can call `search_problem_bank(query)` or `get_problem_bank_summary()`; those tools run locally against the JSON bank. The backend then submits tool results in a second completion request.
- Recent conversation history is limited to 12 messages to control token cost and context growth.
- If no API key is configured, the interface returns a clear setup message instead of silently failing.

### 6. Algorithm visualization

The visualizer is currently intentionally scoped to Two Sum. Each approach declares a visualization type in its question JSON. `data/visualization_traces.py` generates structured Python traces for default data, while `static/js/visualization-player.js` can generate a fresh trace from custom array/target input.

Each trace step contains the current source line, variable values, a main and secondary data structure, a text explanation, and workflow state. The browser renderer maps that contract to an array or HashMap display, highlights code, and exposes play/pause/next/previous/reset, speed, seek, modal, and resizable-panel controls.

The key abstraction is the **trace schema**, not Two Sum itself. To visualize another algorithm, define its visualization metadata and add a trace builder that produces the same step contract.

## Important implementation details

| Component | Technical point worth explaining in an interview |
| --- | --- |
| Flask app | `before_request` loads the current user into `g`; context processors make user and derived site stats available to all templates. |
| SQLite | The project uses two local SQLite files: `progress.db` for accounts, progress, and teaching sessions; `conversations.db` for interview memory. SQLite suits a lightweight single-instance portfolio app with no database service to provision. |
| Data access | SQL statements use parameter placeholders for user input. The code opens and closes a connection per operation, which is simple and safe for this scale. |
| Content loading | Questions are reloaded from disk through `get_topics()` rather than cached. That makes edits immediately visible in development, at the cost of repeated file I/O on every request. |
| UI | Jinja handles initial rendering and vanilla JavaScript handles local interaction. No SPA framework or client-side state library is required. |
| Security choices | Password hashing, ORM-free parameterized SQL, signed Flask sessions, OAuth state handling from Authlib, and same-host redirect validation are present. |
| Tests | Two `unittest` tests check the visualization trace contract and the required template layout hooks. Run them with `python -m unittest discover -s tests -v`. |

## Project structure

```text
app.py                         Flask routes, session handling, APIs, SMTP helper
data/
  auth.py                      User creation, Google identity linking, password checks
  progress.py                  Progress schema, migration, visits, upserts, reset
  chat.py                      Persistent deterministic teacher-chat sessions
  teacher.py                   Rule-based teaching responses and intent detection
  interview_agent.py           OpenAI/Cohere request adapter and local LLM tools
  memory.py                    Interview transcript persistence and language hinting
  questions.py                 Topic metadata and JSON question discovery/loading
  visualization_traces.py      Server-side Two Sum trace generation
  question_data/               150 problem records organised by topic
templates/                     Jinja pages and page-specific JavaScript
static/css/visualization.css   Visualization styling and responsive layout
static/js/visualization-player.js
tests/                         Visualization contract/layout tests
clear_app_data.py              Local development data reset utility
```

## Main routes and APIs

| Route | Purpose |
| --- | --- |
| `GET /`, `/topic/<slug>`, `/question/<slug>/<index>` | Browse topics and authenticated question detail pages. |
| `GET /completed`, `/tricky` | Show the current user’s filtered progress lists. |
| `GET, POST /login`, `GET, POST /signup`, `GET /logout` | Password account flow. |
| `GET /login/google`, `GET /auth/google` | Google OAuth flow. |
| `GET /api/topics` | Return topic/question metadata plus current progress. |
| `POST /api/progress/<progress_key>` | Upsert solved state, tricky flag, and remarks. |
| `POST /api/conversation` | Persist an interview exchange and return the interviewer reply. |
| `POST /api/chat/start`, `POST /api/chat/<id>/message` | Create and continue a saved teacher-chat session. |
| `GET, DELETE /api/chat/<id>` | Retrieve or remove a teacher-chat session after ownership verification. |
| `GET /live-interview` | Render the random-problem mock interview screen. |

## Run locally

Requirements: Python 3.10+ is recommended (the source uses modern type-union syntax).

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>. To run the included tests:

```bash
python -m unittest discover -s tests -v
```

### Configuration

Create a local `.env` file; do not commit it. Only `SECRET_KEY` is necessary for a safe local session setup. OAuth, email, and the external interviewer are optional.

```dotenv
SECRET_KEY=a-long-random-secret

# Google OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Choose one interview provider (optional)
OPENAI_API_KEY=...
# COHERE_API_KEY=...
# LLM_PROVIDER=cohere

# Optional overrides
# LLM_MODEL=gpt-4o-mini
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_TEMPERATURE=0.5

# Optional SMTP confirmation email
# SMTP_SERVER=smtp.example.com
# SMTP_PORT=587
# SMTP_USERNAME=...
# SMTP_PASSWORD=...
```

For a fresh local demo, `python clear_app_data.py --keep-users` clears progress and conversations while retaining accounts. Omitting `--keep-users` also removes local users.

## Interview-ready explanation

### 60-second answer

> I built ReetCode, a Flask-based DSA practice platform that combines a JSON-driven problem bank with authenticated progress tracking and two learning modes. The teaching mode is deterministic and persists topic-based sessions in SQLite, while the live-interview mode uses an OpenAI- or Cohere-compatible API with local problem-bank tools so the model stays grounded in my own content. I also built a trace-driven Two Sum visualizer that synchronizes data-structure state, variables, explanations, and highlighted Java code. I chose server-rendered Jinja plus targeted vanilla JavaScript to keep the app simple, fast to iterate on, and easy to deploy as a single service.

### Questions you should be ready for

1. **Why Flask and server-rendered templates instead of React?** The app is content- and form-centric, so Jinja provides SEO-friendly initial HTML and a low-complexity deployment. I use small `fetch` calls only where live interaction matters. A richer multi-user real-time product could justify a separate SPA API.
2. **Why JSON for questions instead of tables?** Question content is nested and largely editorial: approaches, examples, code, and interview Q&A map naturally to JSON. This removes migration friction for a curated bank. If I needed search, authoring permissions, analytics, or frequent updates, I would normalize metadata into a database or use a CMS.
3. **How is progress isolated per user?** The composite `(progress_key, user_id)` primary key makes one user’s state independent from another’s. The upsert atomically updates status and notes for that key.
4. **Why is the LLM grounded with local tools?** The prompt alone may cause hallucinated or generic problem references. Local search and summaries give the model trusted, current project content while keeping retrieval logic under backend control.
5. **How do you control LLM cost and latency?** History is bounded to 12 messages, the model/temperature/base URL are configurable, requests have a timeout, and tool use makes at most one extra completion pass.
6. **How do the OpenAI and Cohere implementations stay portable?** `LLMConfig` separates provider settings from interview behaviour. The agent converts one logical message/tool contract into the provider’s payload format, so switching providers is environment configuration rather than a UI rewrite.
7. **How does the visualization avoid being tightly coupled to a page?** The player consumes a generic trace: current line, variables, structures, explanation, and workflow node. Adding an algorithm means writing a new trace builder matching that contract, not a new player.
8. **What are the complexity trade-offs shown by Two Sum?** Brute force is `O(n²)` time / `O(1)` space. Sorting plus two pointers is `O(n log n)` time and needs index preservation. The HashMap method is expected `O(n)` time / `O(n)` extra space and preserves original indices naturally.
9. **How do you protect passwords and OAuth navigation?** Passwords use Werkzeug hashes; OAuth is delegated to Authlib/OIDC; post-login destinations are checked against the current host before redirecting.
10. **How would you scale the data layer?** Replace per-operation SQLite connections with a managed relational database and connection pooling, introduce migrations, cache content/search indexes, and move expensive LLM calls to background or streaming infrastructure.
11. **What would you test next?** Route authorization, input validation, database migration/upsert behaviour, OAuth callback failure cases, mock provider/tool-call flows, and browser-level tests for progress and visualization controls.
12. **What was the most interesting engineering decision?** Separating teacher and interviewer personas. It prevents the common UX failure of one generic chatbot alternately over-explaining and acting like an evaluator.

## Honest limitations and production hardening

These are useful interview discussion points, not hidden weaknesses. Identifying them shows ownership of the system design.

- `app.run(debug=True, port=5000)` is development-only. Production should use a WSGI server, environment-selected host/port, `debug=False`, and a required high-entropy secret key.
- Sensitive state-changing routes should require authentication consistently. In particular, progress and interview-memory APIs currently permit anonymous access (which maps progress to user ID `0`), while teacher-chat APIs do enforce it.
- Add CSRF protection and make destructive actions such as progress reset use authenticated `POST` requests instead of `GET`.
- Enable `PRAGMA foreign_keys = ON` for every SQLite connection, then rely on the declared cascade constraints rather than manually deleting dependent rows.
- Validate API payload sizes, topic slugs, progress keys, and question context server-side; rate-limit sign-in and LLM endpoints; and add clear LLM usage quotas.
- The live interview chooses a random client-visible problem and sends client-provided context. A production version should select and validate the question server-side, associate interview transcripts with the authenticated user, and check transcript ownership.
- The question loader reads all JSON files per request. Cache immutable content or pre-index it once the bank grows.
- The teacher’s intent detection is keyword based and intentionally deterministic. It is reliable for a demo but limited in language understanding; a configurable retrieval/LLM layer could improve it.
- Visualization currently covers only Two Sum, and its custom parser accepts a simple `nums = [...] , target = ...` format. Broader algorithm support needs additional trace builders and schema-level tests.
- The supplied tests cover visualization structure only. Add unit, integration, security, and end-to-end coverage before presenting the project as production-ready.

## Suggested next milestones

1. Secure all API routes, add CSRF protection, production configuration, and rate limiting.
2. Add question-schema validation and an authoring/import workflow.
3. Expand the generic visualizer to sliding window, binary search, BFS/DFS, and dynamic-programming tables.
4. Add test coverage for authentication, progress ownership, LLM adapters, and full browser flows.
5. Deploy behind a production WSGI server with managed Postgres and observability for LLM failures, latency, and cost.
