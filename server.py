from flask import Flask, send_file, render_template, request, session, redirect, url_for
import random
from config.config import SECRET_KEY
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
app.secret_key = SECRET_KEY

# GPIO setup
GPIO.setmode(GPIO.BCM)  # BCM pin numbering
relay_pin = 17           # GPIO pin connected to the relay
GPIO.setup(relay_pin, GPIO.OUT)  # Set the pin as an output

def trigger_relay():
    GPIO.output(relay_pin, True)  # Activate the relay (turn on the solenoid valve)
    time.sleep(5)                 # Keep the solenoid valve activated for 5 seconds
    GPIO.output(relay_pin, False) # Deactivate the relay (turn off the solenoid valve)

# Initialize user's bankroll within a before-request handler
@app.before_request
def before_request():
    if 'bankroll' not in session:
        session['bankroll'] = 1000

# Endpoint to check the status of the server
@app.route('/status')
def status():
    return "<h1>Status: Server is running</h1>"

# Endpoint to display the betting form and handle bet submissions
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
            trigger_relay()  # Trigger the relay if the user wins
        else:
            session['bankroll'] -= bet_amount
            result_text = f"You lost ${bet_amount}!"

        return render_template('result.html', result=result.capitalize(), result_text=result_text, bankroll=session['bankroll'])

    return render_template('bet.html', bankroll=session['bankroll'])

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
