let current = 0;
let answers = {};
let timerId = null;
let timeLeft = 60;

function shuffle(a) {
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
}

function renderQuestion(idx) {
    const q = QUESTIONS[idx];
    const area = document.getElementById('question-area');
    let opts = q.options.slice();
    shuffle(opts);
    let html = `<div><h4>Question ${idx+1} / ${QUESTIONS.length}</h4>`;
    html += `<p>${q.question}</p>`;
    html += `<div id="timer" class="mb-2">Time left: <span>${timeLeft}</span>s</div>`;
    html += '<div class="list-group">';
    opts.forEach(o => {
        const checked = answers[idx] === o ? 'checked' : '';
        html += `<label class="list-group-item"><input type="radio" name="opt" value="${o}" ${checked}> ${o}</label>`;
    });
    html += '</div></div>';
    area.innerHTML = html;
}

function startTimer() {
    clearInterval(timerId);
    timeLeft = 60;
    document.getElementById('timer').querySelector('span').textContent = timeLeft;
    timerId = setInterval(() => {
        timeLeft--;
        const el = document.getElementById('timer').querySelector('span');
        el.textContent = timeLeft;
        if (timeLeft <= 0) {
            // auto move to next
            saveAnswerAndAdvance();
        }
    }, 1000);
}

function saveAnswerAndAdvance() {
    const sel = document.querySelector('input[name="opt"]:checked');
    if (sel) answers[current] = sel.value;
    if (current < QUESTIONS.length - 1) {
        current++;
        renderQuestion(current);
        startTimer();
    } else {
        clearInterval(timerId);
        submitExam();
    }
}

function submitExam() {
    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answers })
    }).then(r => r.json()).then(data => {
        alert('Your score: ' + data.score + '/10');
        window.location = '/';
    });
}

window.addEventListener('load', () => {
    renderQuestion(0);
    startTimer();
    document.getElementById('nextBtn').addEventListener('click', () => {
        const sel = document.querySelector('input[name="opt"]:checked');
        if (sel) answers[current] = sel.value;
        if (current < QUESTIONS.length - 1) current++;
        renderQuestion(current);
        startTimer();
    });
    document.getElementById('prevBtn').addEventListener('click', () => {
        const sel = document.querySelector('input[name="opt"]:checked');
        if (sel) answers[current] = sel.value;
        if (current > 0) current--;
        renderQuestion(current);
        startTimer();
    });
    document.getElementById('submitBtn').addEventListener('click', () => {
        const sel = document.querySelector('input[name="opt"]:checked');
        if (sel) answers[current] = sel.value;
        if (confirm('Submit exam now?')) {
            submitExam();
        }
    });
});