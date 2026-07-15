# DSA Interview Prep — Google SWE2/3

A beautiful, topic-wise DSA solutions website built with Python/Flask.  
Java solutions with full approach evolution — brute force → optimal.

## Run locally

```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

## Deploy to Railway / Render / Fly.io

```bash
# Add a Procfile:
echo "web: python app.py" > Procfile

# Set PORT env var in your platform, then update app.py:
# app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

## Project structure

```
dsa-prep/
├── app.py               # Flask routes
├── data/
│   └── questions.py     # All question data (add new topics/questions here)
├── templates/
│   ├── base.html        # Layout, nav, design system
│   ├── index.html       # Homepage
│   ├── topic.html       # Topic question list
│   └── question.html    # Individual question detail
└── requirements.txt
```

## Adding new questions

In `data/questions.py`, add to the relevant topic's `questions` list, or create a new topic entry in `TOPICS`. Follow the existing structure.
