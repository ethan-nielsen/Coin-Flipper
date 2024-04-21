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
    print("Activating the relay...")
    relay_line.set_value(1)
    time.sleep(5)
    relay_line.set_value(0)
    print("Deactivating the relay...")

@app.route('/bet', methods=['GET', 'POST'])
def bet():
    if 'bankroll' not in session:
        session['bankroll'] = 1000  # Ensure bankroll is initialized

    if request.method == 'POST':
        bet_amount = int(request.form.get('bet_amount', 0))
        bet_on = request.form.get('bet_on', '')

        if not bet_amount or not bet_on:
            # Error handling if fields are not properly filled
            return render_template('bet.html', error="Please fill all fields correctly.", bankroll=session['bankroll'])

        # Trigger the relay as soon as a bet is placed, before calculating the result
        trigger_relay()

        # Processing the bet
        result = random.choice(['Heads', 'Tails'])
        session['result'] = result
        session['bet_on'] = bet_on
        session['bet_amount'] = bet_amount

        if result == bet_on:
            session['bankroll'] += bet_amount
            session['result_text'] = "You won!"
        else:
            session['bankroll'] -= bet_amount
            session['result_text'] = f"You lost ${bet_amount}!"

        # Redirect to flip-coin to initiate the flipping animation
        return redirect(url_for('flip_coin'))

    return render_template('bet.html', bankroll=session['bankroll'])


@app.route('/status')
def status():
    return "<h1>Status: Server is running</h1>"

@app.route('/flip-coin')
def flip_coin():
    if 'bankroll' not in session:
        session['bankroll'] = 1000  # Ensure 'bankroll' is initialized

    result = random.choice(['Heads', 'Tails'])
    # Render the flipping animation page before showing the result
    return render_template('flipping.html')
    
@app.route('/display-result')
def display_result():
    # Ensure all needed session data is available
    return render_template('result.html', result=session.get('result', 'No flip yet'),
                           result_text=session.get('result_text', 'Try flipping the coin!'), 
                           bankroll=session.get('bankroll', 1000))


@app.route('/top-up', methods=['GET', 'POST'])
def top_up():
    if request.method == 'POST':
        amount = int(request.form.get('top_up_amount', 0))
        if amount:
            session['bankroll'] += amount
        return redirect(url_for('bet'))

    return render_template('top_up.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
