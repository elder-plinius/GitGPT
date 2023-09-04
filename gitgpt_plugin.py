from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GITHUB_API_BASE_URL = "https://api.github.com"

@app.route('/createRepo', methods=['POST'])
def create_repo():
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    
    headers = {'Authorization': f'token {github_pat}'}
    payload = {'name': repo_name}
    
    response = requests.post(f"{GITHUB_API_BASE_URL}/user/repos", json=payload, headers=headers)
    
    return jsonify(response.json()), response.status_code

@app.route('/editFile', methods=['POST'])
def edit_file():
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    content = request.json.get('content')
    
    headers = {'Authorization': f'token {github_pat}'}
    
    # Fetch the file to get its SHA
    response = requests.get(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/contents/{file_path}", headers=headers)
    file_sha = response.json().get('sha')
    
    payload = {'path': file_path, 'message': 'Edit file via GitGPT', 'content': content, 'sha': file_sha}
    
    response = requests.put(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/contents/{file_path}", json=payload, headers=headers)
    
    return jsonify(response.json()), response.status_code

@app.route('/pushCode', methods=['POST'])
def push_code():
    github_pat = request.json.get('githubPAT')
    repo_name = request.json.get('repoName')
    file_path = request.json.get('filePath')
    new_content = request.json.get('newContent')
    branch = request.json.get('branch', 'main')
    
    headers = {'Authorization': f'token {github_pat}'}
    
    # Step 1: Get latest commit SHA
    response = requests.get(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/git/refs/heads/{branch}", headers=headers)
    latest_commit_sha = response.json()['object']['sha']
    
    # Step 2: Get blob SHA
    response = requests.get(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/contents/{file_path}", headers=headers)
    blob_sha = response.json()['sha']
    
    # Step 3: Create new tree
    tree = [
        {
            "path": file_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
            "content": new_content
        }
    ]
    payload = {"base_tree": latest_commit_sha, "tree": tree}
    response = requests.post(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/git/trees", json=payload, headers=headers)
    tree_sha = response.json()['sha']
    
    # Step 4: Create new commit
    payload = {
        "message": "Update via GitGPT",
        "parents": [latest_commit_sha],
        "tree": tree_sha
    }
    response = requests.post(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/git/commits", json=payload, headers=headers)
    new_commit_sha = response.json()['sha']
    
    # Step 5: Update reference
    payload = {"sha": new_commit_sha}
    response = requests.patch(f"{GITHUB_API_BASE_URL}/repos/{repo_name}/git/refs/heads/{branch}", json=payload, headers=headers)
    
    return jsonify(response.json()), response.status_code


if __name__ == '__main__':
    app.run(port=3000)
