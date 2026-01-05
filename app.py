from flask import Flask, render_template, request, send_file
import os
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Import functions directly from your main.py
from main import clone_repo, list_files, generate_readme, save_readme

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixed folder for generated files
GENERATED_DIR = os.path.join(os.getcwd(), "generated_files")
os.makedirs(GENERATED_DIR, exist_ok=True)


class GenerateReadmeForm(FlaskForm):
    repo_url = StringField('GitHub Repository URL', validators=[DataRequired()])
    submit = SubmitField('Generate README')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = GenerateReadmeForm()
    readme_path = None

    if request.method == 'POST' and form.validate_on_submit():
        repo_url = form.repo_url.data
        try:
            # Clone repo (OS-safe)
            repo_path = clone_repo(repo_url)
            if not repo_path:
                return "Error cloning repository. Check the URL or environment.", 500

            # List files
            files = list_files(repo_path)

            # Generate README content
            repo_name = repo_url.rstrip("/").split("/")[-1]
            readme_content = generate_readme(files, repo_name)

            # Save README
            readme_path = save_readme(readme_content)

        except Exception as e:
            logger.error("Error generating README: %s", e)
            return f"Error generating README: {e}", 500
        finally:
            # Cleanup cloned repo
            if repo_path and os.path.exists(repo_path):
                import shutil
                shutil.rmtree(repo_path)

        if readme_path and os.path.exists(readme_path):
            return send_file(os.path.abspath(readme_path), as_attachment=True)

    return render_template('home.html', form=form, readme_generated=False)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(debug=True)
