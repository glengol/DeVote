from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import matplotlib
matplotlib.use('agg')  # Use a non-GUI backend to avoid threading issues with Flask

import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Dictionary to hold questions and their options
questions = {
    "AWS or GCP or AZURE": ["AWS", "GCP", "AZURE"],
    "YAML or JSON": ["YAML", "JSON"]
}

# Empty list to store votes
votes = []

UPLOAD_FOLDER = 'static/uploads'  # Define the folder to save chart images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    name = request.form.get('name')
    return render_template('vote.html', name=name, questions=questions)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    name = request.form.get('name')
    
    # Iterate through questions and store votes
    for question, options in questions.items():
        choice = request.form.get(f'choice_{question}')
        if choice:
            votes.append({"name": name, "question": question, "choice": choice})

    return redirect(url_for('results'))

@app.route('/results')
def results():
    # Calculate vote results
    results = {}
    for question, options in questions.items():
        results[question] = {option: sum(1 for vote in votes if vote['question'] == question and vote['choice'] == option) for option in options}
    
    # Generate and save pie charts
    chart_paths = {}
    for question, result in results.items():
        labels = list(result.keys())
        values = list(result.values())

        fig = plt.figure()
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        
        # Save chart to file
        chart_filename = f"{question.replace(' ', '_')}_chart.png"
        chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
        plt.savefig(chart_path)
        plt.close(fig)

        chart_paths[question] = chart_filename
    
    return render_template('results.html', results=results, chart_paths=chart_paths)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
