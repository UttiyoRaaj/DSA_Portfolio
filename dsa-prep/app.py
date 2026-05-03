from flask import Flask, render_template, jsonify
from data.questions import TOPICS

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", topics=TOPICS)

@app.route("/topic/<topic_slug>")
def topic(topic_slug):
    topic_data = next((t for t in TOPICS if t["slug"] == topic_slug), None)
    if not topic_data:
        return "Topic not found", 404
    return render_template("topic.html", topic=topic_data, all_topics=TOPICS)

@app.route("/question/<topic_slug>/<int:q_index>")
def question(topic_slug, q_index):
    topic_data = next((t for t in TOPICS if t["slug"] == topic_slug), None)
    if not topic_data or q_index >= len(topic_data["questions"]):
        return "Not found", 404
    q = topic_data["questions"][q_index]
    return render_template("question.html", question=q, topic=topic_data, q_index=q_index, all_topics=TOPICS)

@app.route("/api/topics")
def api_topics():
    return jsonify(TOPICS)

@app.route("/practice")
def practice():
    return render_template("practice.html", topics=TOPICS, page='practice')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
