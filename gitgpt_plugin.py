from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS library
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read GitHub PAT from environment variable
github_pat = os.getenv('GITHUB_PAT')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/createRepo', methods=['POST'])
def create_repo():
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName', 'defaultRepoName')
    
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {github_pat}"}
    payload = {"name": repo_name}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return jsonify({"message": "Repo created successfully", "data": response.json()}), 201
    else:
        return jsonify({"message": "Failed to create repo", "error": response.json()}), response.status_code

@app.route('/editFile', methods=['POST'])
def edit_file():
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    content = request.json.get('content')
    
    url = f"https://api.github.com/repos/{repo_name}/{file_path}"
    headers = {"Authorization": f"token {github_pat}"}
    payload = {"content": content}
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return jsonify({"message": "File edited successfully", "data": response.json()}), 200
    else:
        return jsonify({"message": "Failed to edit file", "error": response.json()}), response.status_code

@app.route('/pushCode', methods=['POST'])
def push_code():
    global github_pat
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    content = request.json.get('content')
    commit_message = request.json.get('commitMessage', 'Update via GitGPT')
    
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_pat}"}
    
    # Fetch the file to get its current SHA
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"message": "Failed to fetch file for SHA", "error": response.json()}), response.status_code
    
    file_sha = response.json().get('sha')
    
    payload = {
        "message": commit_message,
        "content": content.encode('utf-8').hex(),
        "sha": file_sha
    }
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return jsonify({"message": "Code pushed successfully", "data": response.json()}), 200
    else:
        return jsonify({"message": "Failed to push code", "error": response.json()}), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
