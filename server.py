from flask import Flask, send_file, render_template, request, session, redirect, url_for
import random
from config.config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize user's bankroll within a before-request handler
@app.before_request
def before_request():
    if 'bankroll' not in session:
        session['bankroll'] = 1000

# Endpoint to check the status of the server
@app.route('/status')
def status():
    return "<h1>Status: Server is running</h1>"

# Endpoint to display the betting form
@app.route('/bet', methods=['GET', 'POST'])
def bet():
    if 'bankroll' not in session:
        session['bankroll'] = 1000
    
    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        bet_on = request.form['bet_on']
        
        result = random.choice(['heads', 'tails'])
        
        if result == bet_on:
            session['bankroll'] += bet_amount
            result_text = "You won!"
        else:
            session['bankroll'] -= bet_amount
            result_text = f"You lost ${bet_amount}!"
        
        return render_template('result.html', result=result.capitalize(), result_text=result_text, bankroll=session['bankroll'])

    return render_template('bet.html', bankroll=session['bankroll'])  # Pass bankroll to the template

# Endpoint to flip a coin
@app.route('/flip-coin')
def flip_coin():
    result = random.choice(['heads', 'tails'])
    result_text = "Heads" if result == "heads" else "Tails"
    return render_template('result.html', result=result.capitalize(), result_text=result_text, bankroll=session['bankroll'])

# Endpoint to top up the bankroll
@app.route('/top-up', methods=['GET', 'POST'])
def top_up():
    if request.method == 'POST':
        amount = int(request.form['top_up_amount'])
        session['bankroll'] += amount
        return redirect(url_for('bet'))  # Redirect to the betting page after topping up
    
    return render_template('top_up.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
