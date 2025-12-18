# Online Examination Portal with Timed Questions

Simple Flask app demonstrating a timed-question online exam.

Quick start:

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
set FLASK_APP=app.py
flask run
```

3. Open `http://127.0.0.1:5000/`

Notes:
- Instructor login is demo-only (password in app config).
- Questions are fetched from Open Trivia DB API.
