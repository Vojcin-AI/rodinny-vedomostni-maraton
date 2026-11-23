#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import uuid
import secrets
from datetime import datetime
import os
from pathlib import Path
import qrcode
from io import BytesIO
import base64
import re
import time

app = Flask(__name__)
app.secret_key = 'rodinny_kviz_2024'
CORS(app)

# ============================================================================
# DATA STORAGE
# ============================================================================

class QuizData:
    def __init__(self):
        self.teams = {}  # team_id: {name, score, answers}
        self.team_access_codes = {}
        self.current_question = None
        self.current_question_started_at = None
        self.question_index = 0
        self.quiz_state = 'waiting'  # waiting, playing, finished
        self.questions = []
        self.start_time = None
        self.admin_password = 'admin123'
        self.load_quiz()
    
    def load_quiz(self):
        """Načti sample otázky"""
        self.questions = [
            {
                'id': 1,
                'text': 'Jak se jmenuje hlavní postava v pohádce "Tři oříšky"?',
                'type': 'text',
                'correct_answers': ['matěj', 'maťej', 'matej'],
                'points': 1
            },
            {
                'id': 2,
                'text': 'Jaké jméno má postava ze "Zlatovlásky"?',
                'type': 'text',
                'correct_answers': ['božena', 'bozena'],
                'points': 1
            },
            {
                'id': 3,
                'text': 'Kterou pohádkou se rozumí "Popelka"?',
                'type': 'text',
                'correct_answers': ['popelka'],
                'points': 1
            },
            {
                'id': 4,
                'text': 'Kolik měla Popelka sester?',
                'type': 'text',
                'correct_answers': ['2', 'dvě', 'dve'],
                'points': 1
            },
            {
                'id': 5,
                'text': 'Jaké jméno má postava ze "Zvídavého Jiřího"?',
                'type': 'text',
                'correct_answers': ['jiří', 'jiri', 'jiří', 'jiří'],
                'points': 1
            }
        ]
    
    def normalize_answer(self, text):
        """Normalizuj odpověď: lowercase, bez diakritiky"""
        text = text.lower().strip()
        # Odstranění diakritiky
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ů': 'u',
            'č': 'c', 'ř': 'r', 'š': 's', 'ť': 't', 'ž': 'z', 'ď': 'd', 'ň': 'n'
        }
        for accented, plain in replacements.items():
            text = text.replace(accented, plain)
        return text
    
    def check_answer(self, user_answer, correct_answers):
        """Zkontroluj odpověď s tolerancí"""
        normalized_user = self.normalize_answer(user_answer)
        normalized_correct = [self.normalize_answer(ans) for ans in correct_answers]
        return normalized_user in normalized_correct
    
    def register_team(self, team_name):
        """Zaregistruj tým"""
        team_id = str(uuid.uuid4())[:8]
        self.teams[team_id] = {
            'name': team_name,
            'score': 0,
            'total_response_time_seconds': 0.0,
            'answers': {},
            'login_code': None,
            'typing_question_id': None,
            'last_activity_at': None,
            'registered_at': datetime.now().isoformat()
        }
        return team_id

    def create_team_with_login_code(self, team_name):
        """Vytvoř předem tým s kódem pro přihlášení."""
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        login_code = ''.join(secrets.choice(alphabet) for _ in range(8))
        while login_code in self.team_access_codes:
            login_code = ''.join(secrets.choice(alphabet) for _ in range(8))

        team_id = self.register_team(team_name)
        self.teams[team_id]['login_code'] = login_code
        self.team_access_codes[login_code] = team_id
        return team_id, login_code
    
    def submit_answer(self, team_id, question_id, answer, response_time_seconds):
        """Odešli odpověď od týmu"""
        if team_id not in self.teams:
            return False
        
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if not question:
            return False
        
        is_correct = self.check_answer(answer, question['correct_answers'])
        
        self.teams[team_id]['answers'][question_id] = {
            'answer': answer,
            'is_correct': is_correct,
            'points': question['points'] if is_correct else 0,
            'response_time_seconds': response_time_seconds,
            'submitted_at': datetime.now().isoformat()
        }
        self.teams[team_id]['total_response_time_seconds'] += response_time_seconds
        
        # Přidej body
        if is_correct:
            self.teams[team_id]['score'] += question['points']
        
        return is_correct
    
    def get_leaderboard(self):
        """Vrátí leaderboard seřazený"""
        sorted_teams = sorted(
            self.teams.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        return [
            {
                'position': i + 1,
                'team_id': tid,
                'name': t['name'],
                'score': t['score'],
                'answers_count': len(t['answers']),
                'total_response_time_seconds': (
                    round(t['total_response_time_seconds'], 2)
                    if t['answers']
                    else None
                )
            }
            for i, (tid, t) in enumerate(sorted_teams)
        ]

quiz_data = QuizData()

# ============================================================================
# ROUTES - ADMIN
# ============================================================================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin přihlášení"""
    data = request.json
    if data.get('password') == quiz_data.admin_password:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Špatné heslo'}), 401

@app.route('/api/admin/start-quiz', methods=['POST'])
def admin_start_quiz():
    """Spusť kvíz"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Reset otázek, ale ZACHOVAT registrované týmy!
    quiz_data.quiz_state = 'playing'
    quiz_data.question_index = 0
    quiz_data.current_question = None
    quiz_data.current_question_started_at = None
    quiz_data.start_time = datetime.now().isoformat()
    
    # Resetuj jen odpovědi, ne týmy samotné
    for team_id in quiz_data.teams:
        quiz_data.teams[team_id]['answers'] = {}
        quiz_data.teams[team_id]['score'] = 0
        quiz_data.teams[team_id]['total_response_time_seconds'] = 0.0
        quiz_data.teams[team_id]['typing_question_id'] = None
        quiz_data.teams[team_id]['last_activity_at'] = None
    
    return jsonify({'success': True, 'message': 'Kvíz spuštěn!'})

@app.route('/api/admin/next-question', methods=['POST'])
def admin_next_question():
    """Jdi na další otázku"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    if quiz_data.current_question:
        question_id = quiz_data.current_question['id']
        unanswered = [
            team['name']
            for team in quiz_data.teams.values()
            if question_id not in team['answers']
        ]
        if unanswered:
            return jsonify({
                'success': False,
                'error': 'Na odpověď ještě čeká část týmů.',
                'unanswered_teams': unanswered
            }), 409
    
    if quiz_data.question_index < len(quiz_data.questions):
        quiz_data.current_question = quiz_data.questions[quiz_data.question_index]
        quiz_data.question_index += 1
        quiz_data.current_question_started_at = time.monotonic()
        for team in quiz_data.teams.values():
            team['typing_question_id'] = None
            team['last_activity_at'] = None
        return jsonify({
            'success': True,
            'question': quiz_data.current_question,
            'question_number': quiz_data.question_index,
            'total_questions': len(quiz_data.questions)
        })
    else:
        quiz_data.quiz_state = 'finished'
        quiz_data.current_question_started_at = None
        return jsonify({
            'success': False,
            'message': 'Všechny otázky zodpovězeny!',
            'quiz_state': 'finished'
        })

@app.route('/api/admin/end-quiz', methods=['POST'])
def admin_end_quiz():
    """Ukonči kvíz"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    quiz_data.quiz_state = 'finished'
    quiz_data.current_question_started_at = None
    leaderboard = quiz_data.get_leaderboard()
    return jsonify({
        'success': True,
        'leaderboard': leaderboard
    })

@app.route('/api/admin/leaderboard', methods=['GET'])
def admin_leaderboard():
    """Vrátí leaderboard"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    teams = quiz_data.get_leaderboard()
    current_question_id = (
        quiz_data.current_question['id'] if quiz_data.current_question else None
    )
    answered_count = 0

    for team in teams:
        team_data = quiz_data.teams[team['team_id']]
        team['login_code'] = team_data['login_code']
        if quiz_data.quiz_state != 'playing' or current_question_id is None:
            team['answer_status'] = 'inactive'
        elif current_question_id in team_data['answers']:
            team['answer_status'] = 'answered'
            answered_count += 1
        elif (
            team_data.get('typing_question_id') == current_question_id
            and team_data.get('last_activity_at') is not None
            and datetime.now().timestamp() - team_data['last_activity_at'] <= 10
        ):
            team['answer_status'] = 'typing'
        else:
            team['answer_status'] = 'waiting'

    return jsonify({
        'leaderboard': teams,
        'quiz_state': quiz_data.quiz_state,
        'answered_count': answered_count,
        'registered_count': len(teams),
        'all_answered': bool(teams) and answered_count == len(teams)
    })

@app.route('/api/leaderboard', methods=['GET'])
def public_leaderboard():
    """Veřejné skóre bez interních stavů a přihlašovacích kódů."""
    return jsonify({
        'leaderboard': quiz_data.get_leaderboard(),
        'quiz_state': quiz_data.quiz_state
    })

@app.route('/api/admin/teams', methods=['POST'])
def admin_create_team():
    """Přidej tým před začátkem hry a vydej mu přihlašovací kód."""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    if quiz_data.quiz_state != 'waiting':
        return jsonify({'error': 'Nové týmy lze přidávat jen před začátkem kvízu.'}), 409

    data = request.json or {}
    team_name = data.get('team_name', '').strip()
    if not team_name:
        return jsonify({'error': 'Jméno týmu je povinné.'}), 400
    if len(team_name) > 30:
        return jsonify({'error': 'Jméno týmu může mít nejvýše 30 znaků.'}), 400

    team_id, login_code = quiz_data.create_team_with_login_code(team_name)
    return jsonify({
        'success': True,
        'team_id': team_id,
        'team_name': team_name,
        'login_code': login_code
    })

@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    """Reset kvízu"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    quiz_data.teams = {}
    quiz_data.team_access_codes = {}
    quiz_data.current_question = None
    quiz_data.current_question_started_at = None
    quiz_data.question_index = 0
    quiz_data.quiz_state = 'waiting'
    quiz_data.start_time = None
    
    return jsonify({'success': True, 'message': 'Kvíz resetován'})

@app.route('/api/admin/qr-code', methods=['GET'])
def generate_qr():
    """Vygeneruj QR kód pro týmy"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Vytvoř QR pro odkaz na registraci
    qr_url = request.host_url.rstrip('/') + '/team'
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Konvertuj na base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({
        'qr_code': f'data:image/png;base64,{img_base64}',
        'url': qr_url
    })

# ============================================================================
# ROUTES - TEAM
# ============================================================================

@app.route('/api/team/register', methods=['POST'])
def team_register():
    """Zaregistruj tým"""
    if quiz_data.quiz_state != 'waiting':
        return jsonify({'error': 'Registrace nových týmů je uzavřena.'}), 409

    data = request.json or {}
    team_name = data.get('team_name', '').strip()
    
    if not team_name:
        return jsonify({'error': 'Jméno týmu je povinné'}), 400
    
    team_id = quiz_data.register_team(team_name)
    
    return jsonify({
        'success': True,
        'team_id': team_id,
        'message': f'Tým "{team_name}" zaregistrován!'
    })

@app.route('/api/team/login', methods=['POST'])
def team_login():
    """Přihlas tým vytvořený administrátorem."""
    data = request.json or {}
    login_code = data.get('login_code', '').strip().upper()
    team_id = quiz_data.team_access_codes.get(login_code)
    if not team_id:
        return jsonify({'error': 'Přihlašovací kód nebyl nalezen.'}), 404

    return jsonify({
        'success': True,
        'team_id': team_id,
        'team_name': quiz_data.teams[team_id]['name']
    })

@app.route('/api/team/status', methods=['GET'])
def team_status():
    """Vrátí status kvízu pro tým"""
    return jsonify({
        'quiz_state': quiz_data.quiz_state,
        'current_question': quiz_data.current_question,
        'question_number': quiz_data.question_index,
        'total_questions': len(quiz_data.questions)
    })

@app.route('/api/team/activity', methods=['POST'])
def team_activity():
    """Označ tým jako rozepisující odpověď na aktuální otázku."""
    data = request.json or {}
    team_id = data.get('team_id')
    question_id = data.get('question_id')

    if team_id not in quiz_data.teams:
        return jsonify({'error': 'Tým nenalezen'}), 404
    if (
        quiz_data.quiz_state != 'playing'
        or not quiz_data.current_question
        or question_id != quiz_data.current_question['id']
    ):
        return jsonify({'error': 'Tato otázka už není aktivní'}), 409
    if question_id in quiz_data.teams[team_id]['answers']:
        return jsonify({'error': 'Odpověď už byla odeslána'}), 409

    team = quiz_data.teams[team_id]
    team['typing_question_id'] = question_id
    team['last_activity_at'] = datetime.now().timestamp()
    return jsonify({'success': True})

@app.route('/api/team/submit-answer', methods=['POST'])
def team_submit_answer():
    """Odešli odpověď"""
    data = request.json or {}
    team_id = data.get('team_id')
    question_id = data.get('question_id')
    answer = data.get('answer', '').strip()
    
    if not team_id or not question_id or not answer:
        return jsonify({'error': 'Chybí požadované údaje'}), 400
    
    if team_id not in quiz_data.teams:
        return jsonify({'error': 'Tým nenalezen'}), 404

    if (
        quiz_data.quiz_state != 'playing'
        or not quiz_data.current_question
        or question_id != quiz_data.current_question['id']
    ):
        return jsonify({'error': 'Tato otázka už není aktivní'}), 409

    if question_id in quiz_data.teams[team_id]['answers']:
        return jsonify({'error': 'Odpověď už byla odeslána'}), 409
    
    if quiz_data.current_question_started_at is None:
        return jsonify({'error': 'Čas otázky se nepodařilo načíst. Kontaktuj moderátora.'}), 409
    response_time_seconds = round(
        max(0.0, time.monotonic() - quiz_data.current_question_started_at), 2
    )
    is_correct = quiz_data.submit_answer(
        team_id, question_id, answer, response_time_seconds
    )
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'score': quiz_data.teams[team_id]['score'],
        'response_time_seconds': response_time_seconds,
        'total_response_time_seconds': round(
            quiz_data.teams[team_id]['total_response_time_seconds'], 2
        ),
        'message': 'Správně!' if is_correct else 'Bohužel špatně'
    })

@app.route('/api/team/score/<team_id>', methods=['GET'])
def team_score(team_id):
    """Vrátí skóre týmu"""
    if team_id not in quiz_data.teams:
        return jsonify({'error': 'Tým nenalezen'}), 404
    
    team = quiz_data.teams[team_id]
    return jsonify({
        'team_name': team['name'],
        'score': team['score'],
        'total_response_time_seconds': (
            round(team['total_response_time_seconds'], 2)
            if team['answers']
            else None
        ),
        'answers_count': len(team['answers'])
    })

# ============================================================================
# STATIC PAGES
# ============================================================================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin panel"""
    return render_template('admin.html')

@app.route('/team')
def team():
    """Team registration & play page"""
    return render_template('team.html')

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard pro diváky"""
    return render_template('leaderboard.html')

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
