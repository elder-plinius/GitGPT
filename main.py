import json
import quart
import quart_cors
from quart import request, jsonify
from dotenv import load_dotenv
import logging
import requests  # Added this import

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

@app.route('/')
async def root():
    return "GitGPT Plugin is running!"

@app.route('/createRepo', methods=['POST'])
async def create_repo():
    logging.debug("Entered /createRepo")
    github_pat = (await request.json).get('githubPAT')
    repo_name = (await request.json).get('repoName', 'defaultRepoName')
    
    headers = {
        'Authorization': f'token {github_pat}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': repo_name
    }
    
    response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
    
    if response.status_code == 201:
        return jsonify({"message": "Repository created successfully", "repo_url": response.json()['html_url']})
    else:
        return jsonify({"message": "Failed to create repository", "error": response.json()}), 400

@app.route('/editFile', methods=['POST'])
async def edit_file():
    logging.debug("Entered /editFile")
    github_pat = (await request.json).get('githubPAT')
    repo_name = (await request.json).get('repoName')
    file_path = (await request.json).get('filePath')
    new_content = (await request.json).get('newContent')
    
    headers = {
        'Authorization': f'token {github_pat}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(f'https://api.github.com/repos/{repo_name}/contents/{file_path}', headers=headers)
    file_sha = response.json().get('sha')
    
    data = {
        'message': 'Update file via GitGPT',
        'content': new_content.encode('utf-8').decode('utf-8'),
        'sha': file_sha
    }
    
    response = requests.put(f'https://api.github.com/repos/{repo_name}/contents/{file_path}', headers=headers, json=data)
    
    if response.status_code == 200:
        return jsonify({"message": "File updated successfully"})
    else:
        return jsonify({"message": "Failed to update file", "error": response.json()}), 400

@app.route('/pushCode', methods=['POST'])
async def push_code():
    logging.debug("Entered /pushCode")
    github_pat = (await request.json).get('githubPAT')
    repo_name = (await request.json).get('repoName')
    file_path = (await request.json).get('filePath')
    new_content = (await request.json).get('newContent')
    
    headers = {
        'Authorization': f'token {github_pat}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(f'https://api.github.com/repos/{repo_name}/contents/{file_path}', headers=headers)
    file_sha = response.json().get('sha')
    
    data = {
        'message': 'Push code via GitGPT',
        'content': new_content.encode('utf-8').decode('utf-8'),
        'sha': file_sha
    }
    
    response = requests.put(f'https://api.github.com/repos/{repo_name}/contents/{file_path}', headers=headers, json=data)
    
    if response.status_code == 200:
        return jsonify({"message": "Code pushed successfully"})
    else:
        return jsonify({"message": "Failed to push code", "error": response.json()}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
