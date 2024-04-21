from flask import Flask, render_template, request, session, redirect, url_for
import random
from config.config import SECRET_KEY
import gpiod
import time

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Define the GPIO chip and pin
chip = gpiod.Chip('gpiochip4')
relay_pin = 17
relay_line = chip.get_line(relay_pin)
relay_line.request(consumer='relay', type=gpiod.LINE_REQ_DIR_OUT)

def trigger_relay():
    print("Activating the relay...")  # Log when the relay is activated
    relay_line.set_value(1)  # Activate the relay (turn on the solenoid valve)
    time.sleep(5)            # Keep the solenoid valve activated for 5 seconds
    relay_line.set_value(0)  # Deactivate the relay (turn off the solenoid valve)
    print("Deactivating the relay...")  # Log when the relay is deactivated

@app.route('/bet', methods=['GET', 'POST'])
def bet():
    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        bet_on = request.form['bet_on']

        # Trigger the relay as soon as a bet is placed
        trigger_relay()

        result = random.choice(['heads', 'tails'])

        if result == bet_on:
            session['bankroll'] += bet_amount
            result_text = "You won!"
        else:
            session['bankroll'] -= bet_amount
            result_text = f"You lost ${bet_amount}!"

        return render_template('result.html', result=result.capitalize(), result_text=result_text, bankroll=session['bankroll'])

    return render_template('bet.html', bankroll=session['bankroll'])

@app.route('/status')
def status():
    return "<h1>Status: Server is running</h1>"

@app.route('/flip-coin')
def flip_coin():
    result = random.choice(['heads', 'tails'])
    result_text = "Heads" if result == "heads" else "Tails"
    return render_template('result.html', result=result.capitalize(), result_text=result_text, bankroll=session['bankroll'])

@app.route('/top-up', methods=['GET', 'POST'])
def top_up():
    if request.method == 'POST':
        amount = int(request.form['top_up_amount'])
        session['bankroll'] += amount
        return redirect(url_for('bet'))

    return render_template('top_up.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
