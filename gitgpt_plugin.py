from github import Github, GithubException

# Plugin Manifest
manifest = {
    "name": "GitGPT",
    "description": "A plugin that allows ChatGPT to create repos and push code to GitHub.",
    "version": "0.1",
    "options": [
        {
            "name": "github_token",
            "description": "Your GitHub Token",
            "type": "text",
            "required": True
        }
    ]
}

# Core Functionality (GitGPT class)
class GitGPT:
    def __init__(self, github_token):
        self.github_token = github_token
        self.github = Github(self.github_token)

    def create_repository(self, repo_name):
        try:
            user = self.github.get_user()
            user.create_repo(repo_name)
            return {"status": "success", "message": f"Repository '{repo_name}' created."}
        except GithubException as e:
            return {"status": "error", "message": f"Failed to create repository: {e}"}

# API Endpoints
def create_repository(options, payload):
    github_token = options["github_token"]
    repo_name = payload["repo_name"]
    gitgpt = GitGPT(github_token)
    return gitgpt.create_repository(repo_name)

# Register the endpoint
endpoints = {
    "create_repository": create_repository
}
