from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import html
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Simple instructor password for demo
INSTRUCTOR_PASSWORD = os.environ.get('INSTRUCTOR_PASSWORD', 'instructor123')

db = SQLAlchemy(app)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    enrollment = db.Column(db.String(64))
    subject = db.Column(db.String(64))
    score = db.Column(db.Integer)

with app.app_context():
    db.create_all()

SUBJECT_CATEGORIES = {
    'General Knowledge': 9,
    'Science & Nature': 17,
    'Computers': 18,
    'Mathematics': 19,
}

@app.route('/')
def index():
    return render_template('index.html', subjects=list(SUBJECT_CATEGORIES.keys()))

@app.route('/start', methods=['POST'])
def start():
    name = request.form.get('name')
    enrollment = request.form.get('enrollment')
    subject = request.form.get('subject')
    if not (name and enrollment and subject):
        return redirect(url_for('index'))
    session['student'] = {'name': name, 'enrollment': enrollment, 'subject': subject}
    # Fetch 10 questions from OpenTDB
    category = SUBJECT_CATEGORIES.get(subject)
    url = f'https://opentdb.com/api.php?amount=10&category={category}&type=multiple'
    resp = requests.get(url, timeout=10)
    data = resp.json()
    questions = []
    for item in data.get('results', []):
        q = {
            'question': html.unescape(item['question']),
            'correct_answer': html.unescape(item['correct_answer']),
            'options': [html.unescape(x) for x in item['incorrect_answers']] + [html.unescape(item['correct_answer'])]
        }
        # shuffle options client-side for determinism in JS
        questions.append(q)
    session['questions'] = questions
    return render_template('exam.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    student = session.get('student')
    questions = session.get('questions') or []
    answers = request.json.get('answers', {})
    score = 0
    for idx, q in enumerate(questions):
        selected = answers.get(str(idx))
        if selected and selected == q['correct_answer']:
            score += 1
    if student:
        r = Result(name=student['name'], enrollment=student['enrollment'], subject=student['subject'], score=score)
        db.session.add(r)
        db.session.commit()
    # Clear session exam data
    session.pop('questions', None)
    session.pop('student', None)
    return jsonify({'score': score})

@app.route('/result/<int:result_id>')
def view_result(result_id):
    r = Result.query.get_or_404(result_id)
    return render_template('result.html', result=r)

@app.route('/instructor/login', methods=['GET','POST'])
def instructor_login():
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd == INSTRUCTOR_PASSWORD:
            session['instructor'] = True
            return redirect(url_for('instructor_dashboard'))
        else:
            return render_template('instructor_login.html', error='Invalid password')
    return render_template('instructor_login.html')

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if not session.get('instructor'):
        return redirect(url_for('instructor_login'))
    results = Result.query.order_by(Result.id.desc()).all()
    return render_template('instructor_dashboard.html', results=results)

@app.route('/instructor/logout')
def instructor_logout():
    session.pop('instructor', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
