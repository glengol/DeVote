from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Load data
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"votes": []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    name = request.form.get('name')
    return render_template('vote.html', name=name)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    name = request.form.get('name')
    choice = request.form.get('choice')
    data["votes"].append({"name": name, "choice": choice})

    with open('data.json', 'w') as f:
        json.dump(data, f)

    return redirect(url_for('results'))

@app.route('/results')
def results():
    choices = {}
    for vote in data["votes"]:
        choice = vote["choice"]
        if choice in choices:
            choices[choice] += 1
        else:
            choices[choice] = 1
    return render_template('results.html', votes=data["votes"], choices=choices)

if __name__ == '__main__':
    app.run(debug=True)
