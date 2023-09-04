from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
import requests
from dotenv import load_dotenv
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/')
def root():
    return "GitGPT Plugin is running!"

@app.route('/createRepo', methods=['POST'])
def create_repo():
    logging.debug("Entered /createRepo")
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName', 'defaultRepoName')
    
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {github_pat}"}
    payload = {"name": repo_name}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        logging.info("Repo created successfully")
        return jsonify({"message": "Repo created successfully", "data": response.json()}), 201
    else:
        logging.error(f"Failed to create repo: {response.json()}")
        return jsonify({"message": "Failed to create repo", "error": response.json()}), response.status_code

@app.route('/editFile', methods=['POST'])
def edit_file():
    logging.debug("Entered /editFile")
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    content = request.json.get('content')
    
    url = f"https://api.github.com/repos/{repo_name}/{file_path}"
    headers = {"Authorization": f"token {github_pat}"}
    payload = {"content": content}
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        logging.info("File edited successfully")
        return jsonify({"message": "File edited successfully", "data": response.json()}), 200
    else:
        logging.error(f"Failed to edit file: {response.json()}")
        return jsonify({"message": "Failed to edit file", "error": response.json()}), response.status_code

@app.route('/pushCode', methods=['POST'])
def push_code():
    logging.debug("Entered /pushCode")
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    content = request.json.get('content')
    commit_message = request.json.get('commitMessage', 'Update via GitGPT')
    
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_pat}"}
    
    # Fetch the file to get its current SHA
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch file for SHA: {response.json()}")
        return jsonify({"message": "Failed to fetch file for SHA", "error": response.json()}), response.status_code
    
    file_sha = response.json().get('sha')
    
    payload = {
        "message": commit_message,
        "content": content.encode('utf-8').hex(),
        "sha": file_sha
    }
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        logging.info("Code pushed successfully")
        return jsonify({"message": "Code pushed successfully", "data": response.json()}), 200
    else:
        logging.error(f"Failed to push code: {response.json()}")
        return jsonify({"message": "Failed to push code", "error": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
