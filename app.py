from flask import Flask, render_template, request, session, redirect, url_for

from flask_cors import CORS


app = Flask(__name__)



@app.route('/')
def index():
    return render_template('main.html')
@app.route('/analyze_cv')
def analyseCv():
    return render_template('analyzeCV.html')
@app.route('/analyze_job')
def analyseJob():
    return render_template('analyzeJob.html')

    
if __name__ == "__main__":
    app.run(debug=True)
