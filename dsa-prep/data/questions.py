from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parent
QUESTION_DATA_DIR = DATA_DIR / "question_data"

TOPICS_META = [
    {
        "slug": "arrays-hashing",
        "title": "Arrays & Hashing",
        "color": "#00D9FF",
        "icon": "⚡",
    },
    {
        "slug": "two-pointers",
        "title": "Two Pointers",
        "color": "#34c759",
        "icon": "↔️",
    },
    {
        "slug": "sliding-window",
        "title": "Sliding Window",
        "color": "#f6c118",
        "icon": "🪟",
    },
    {
        "slug": "stack",
        "title": "Stack",
        "color": "#8b5cf6",
        "icon": "🗂️",
    },
    {
        "slug": "binary-search",
        "title": "Binary Search",
        "color": "#0ea5e9",
        "icon": "🔍",
    },
    {
        "slug": "linked-list",
        "title": "Linked List",
        "color": "#ec4899",
        "icon": "🔗",
    },
    {
        "slug": "trees",
        "title": "Trees",
        "color": "#22c55e",
        "icon": "🌳",
    },
    {
        "slug": "graphs",
        "title": "Graphs",
        "color": "#6366f1",
        "icon": "🔗",
    },
    {
        "slug": "trie",
        "title": "Trie",
        "color": "#f97316",
        "icon": "🌲",
    },
    {
        "slug": "heap",
        "title": "Heap / Priority Queue",
        "color": "#e11d48",
        "icon": "📊",
    },
    {
        "slug": "backtracking",
        "title": "Backtracking",
        "color": "#0891b2",
        "icon": "🔁",
    },
    {
        "slug": "dynamic-programming",
        "title": "Dynamic Programming",
        "color": "#facc15",
        "icon": "🧠",
    },
    {
        "slug": "greedy",
        "title": "Greedy",
        "color": "#fb7185",
        "icon": "💡",
    },
    {
        "slug": "intervals",
        "title": "Intervals",
        "color": "#10b981",
        "icon": "🧮",
    },
    {
        "slug": "math-bit-manipulation",
        "title": "Math & Bit Manipulation",
        "color": "#f59e0b",
        "icon": "🔢",
    },
    {
        "slug": "design",
        "title": "Design",
        "color": "#7c3aed",
        "icon": "🏗️",
    },
]


def _load_question_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_question_paths(topic_slug: str) -> list[Path]:
    topic_dir = QUESTION_DATA_DIR / topic_slug
    if not topic_dir.exists():
        return []
    return sorted(
        [p for p in topic_dir.glob("*.json") if p.is_file()],
        key=lambda p: p.name,
    )


def _load_topics() -> list[dict]:
    topics = []
    for topic in TOPICS_META:
        questions = [_load_question_file(path) for path in _get_question_paths(topic["slug"])]
        questions.sort(key=lambda q: q.get("id", 0))
        topic_data = topic.copy()
        topic_data["questions"] = questions
        topic_data["total"] = len(questions)
        topics.append(topic_data)
    return topics


def get_topics() -> list[dict]:
    return _load_topics()


TOPICS = get_topics()
