from flask import Flask, jsonify, request, redirect, url_for, render_template, send_file
import subprocess
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

class GenerateReadmeForm(FlaskForm):
    repo_url = StringField('GitHub Repository URL', validators=[DataRequired()])
    submit = SubmitField('Generate README')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = GenerateReadmeForm()
    if request.method == 'POST' and form.validate_on_submit():
        repo_url = form.repo_url.data
        try:
            subprocess.run(["python3", "main.py", "--url", repo_url])
        except subprocess.CalledProcessError:
            return "Error generating README", 500
        send_file_path = os.path.join("generated_files","README.md")
        if os.path.exists(send_file_path):
            return send_file(send_file_path, as_attachment=True)
    return render_template('home.html', form=form, readme_generated=False)

if __name__ == "__main__":
    app.run(debug=True)
