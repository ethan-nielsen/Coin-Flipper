from flask import Flask, render_template, request, session, redirect, url_for
import random
import gpiod
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
        session['bankroll'] = 1000

    if request.method == 'POST':
        bet_amount = int(request.form.get('bet_amount', 0))
        bet_on = request.form.get('bet_on', '')

        if not bet_amount or not bet_on:
            return render_template('bet.html', error="Please fill all fields correctly.", bankroll=session['bankroll'])

        session['bet_amount'] = bet_amount
        session['bet_on'] = bet_on
        session['result'] = random.choice(['Heads', 'Tails'])

        # Check the result of the bet and update the bankroll accordingly
        if session['result'] == session['bet_on']:
            session['bankroll'] += bet_amount
            session['result_text'] = "You won!"
        else:
            session['bankroll'] -= bet_amount
            session['result_text'] = f"You lost ${bet_amount}!"

        return redirect(url_for('flip_coin'))

    return render_template('bet.html', bankroll=session['bankroll'])

@app.route('/trigger-relay', methods=['POST'])
def handle_relay():
    trigger_relay()
    return "Relay deactivated", 200

@app.route('/flip-coin')
def flip_coin():
    return render_template('flipping.html')

@app.route('/display-result')
def display_result():
    return render_template('result.html', 
                           result=session.get('result', 'No flip yet'),
                           result_text=session['bet_on'],
                           bankroll=session.get('bankroll', 1000))

@app.route('/top-up', methods=['GET', 'POST'])
def top_up():
    if request.method == 'POST':
        # Handle the form submission to update the bankroll
        amount = int(request.form.get('top_up_amount', 0))
        if amount > 0:
            session['bankroll'] += amount
        return redirect(url_for('bet'))  # Redirect to the bet page after topping up

    # If it's a GET request, simply render the top-up page
    return render_template('top_up.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
