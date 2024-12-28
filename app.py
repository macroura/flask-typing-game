from flask import Flask, render_template, request, redirect, url_for, session
import random
import datetime
from spellchecker import SpellChecker

# Initialize the spell checker and Flask app
spell = SpellChecker()
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

starters = ['de', 'ab', 'co', 'no', 'ma', 'mi', 'ap', 'al', 'ta', 'da', 'pa', 'la', 'ra', 'to']

def pick_prefix(word):
    """Choose a prefix based on the word."""
    x = random.randint(0, 100)
    if x < 70:
        return word[-3:] if len(word) >= 3 else word
    else:
        return word[-2:] if len(word) >= 2 else word

@app.route('/')
def index():
    session.clear()
    session['highscore'] = session.get('highscore', 0)
    return render_template('index.html', highscore=session['highscore'])

@app.route('/start', methods=['POST'])
def start_game():
    session['current_prefix'] = random.choice(starters)
    session['start_time'] = datetime.datetime.now()
    session['long_word'] = session['current_prefix']
    session['attempts'] = 0
    return redirect(url_for('game'))

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        inp = request.form.get('word')
        current_prefix = session['current_prefix']
        long_word = session['long_word']
        
        # Validate the prefix
        if not inp.lower().startswith(current_prefix.lower()):
            return render_template('game.html', error='Incorrect Prefix!', long_word=long_word, prefix=current_prefix)

        # Validate the word against the dictionary
        if not spell.correction(inp.lower()) == inp.lower():
            return render_template('game.html', error='Invalid Word!', long_word=long_word, prefix=current_prefix)

        # Validate word length
        if len(inp) <= 3:
            return render_template('game.html', error='Word too short!', long_word=long_word, prefix=current_prefix)

        # Update game state
        prefix_length = len(current_prefix)
        session['long_word'] += inp[prefix_length:]
        session['current_prefix'] = pick_prefix(inp)
        session['attempts'] += 1

        # Check for game completion
        if session['attempts'] >= 10:
            return redirect(url_for('end_game'))

    return render_template('game.html', error=None, long_word=session['long_word'], prefix=session['current_prefix'])

@app.route('/end')
def end_game():
    start_time = session['start_time']
    elapsed_time = datetime.datetime.now() - start_time
    score = max(0, 350 - elapsed_time.total_seconds())
    session['highscore'] = max(session['highscore'], score)
    return render_template('end.html', long_word=session['long_word'], score=score, elapsed_time=elapsed_time.total_seconds(), highscore=session['highscore'])

if __name__ == '__main__':
    app.run(debug=True)
