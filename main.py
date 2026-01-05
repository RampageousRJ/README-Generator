import subprocess
import argparse
import openai
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

def clone_repo(repo_url, clone_dir="temp_repo"):
    if os.path.exists(clone_dir):
        logger.info(f"{clone_dir} already exists. Deleting it...")
        subprocess.run(["rm", "-rf", clone_dir])

    logger.info(f"Cloning {repo_url} into {clone_dir}...")
    result = subprocess.run(["git", "clone", repo_url, clone_dir], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Error cloning repo: %s", result.stderr)
        return False
    logger.info("Repository cloned successfully.")
    return clone_dir

def list_files(repo_path):
    file_list = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.js', '.java', '.cpp', '.md', '.txt', '.json', '.yml', '.yaml', '.html', '.css', '.ts', '.go', '.rb', '.php', '.rs')):
                file_list.append(os.path.relpath(os.path.join(root, file), repo_path))
                logger.info("Found file: %s", file)
    return file_list

def generate_readme(file_list, repo_name):
    prompt = f"""
    You are an expert developer. Generate a concise, professional README for the repository '{repo_name}'.
    The repo contains the following files:
    {file_list}

    Include sections like:
    - Project Description
    - Installation Instructions
    - Usage
    - Features
    - License (if any)
    Be concise and clear.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_readme(content):
    output_dir = os.path.join(os.getcwd(), "generated_files")
    os.makedirs(output_dir, exist_ok=True)
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"README.md generated at {readme_path}")
    return readme_path

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Generate README.md for Github Remote URL")
    argparser.add_argument("--url", type=str, required=True, help="The Github Remote URL")
    args = argparser.parse_args()

    repo_path = clone_repo(args.url)
    try:
        if repo_path:
            files = list_files(repo_path)
            readme_content = generate_readme(files, repo_name=args.url.split("/")[-1])
            save_readme(readme_content, repo_path)
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
    finally:
        if repo_path and os.path.exists(repo_path):
            subprocess.run(["rm", "-rf", repo_path])
            logger.info(f"Cleaned up temporary directory {repo_path}.")
    