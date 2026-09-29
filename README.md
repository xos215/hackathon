# NEXA Hackathon Starter

## Stack
- Python + Flask
- SQLite
- HTML/CSS/JavaScript

## Run
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py

Open http://127.0.0.1:5000

## Hackathon workflow
Keep the dashboard shell. Rename the visible labels and change the fields/status values to match the problem statement.

Architecture:
Browser -> JavaScript fetch() -> Flask -> SQLite -> JSON -> Browser
