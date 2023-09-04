from github import Github, InputGitTreeElement

class GitGPT:
    def __init__(self, github_token):
        self.github_token = github_token
        self.github = Github(self.github_token)

    def authenticate(self):
        try:
            user = self.github.get_user()
            print(f"Authenticated as {user.login}")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def create_repository(self, repo_name):
        user = self.github.get_user()
        repo = user.create_repo(repo_name)
        print(f"Repository '{repo_name}' created.")

    def create_file(self, repo_name, file_name, content):
        repo = self.github.get_user().get_repo(repo_name)
        repo.create_file(file_name, f"create {file_name}", content)

    def edit_file(self, repo_name, file_name, content):
        repo = self.github.get_user().get_repo(repo_name)
        file = repo.get_contents(file_name)
        repo.update_file(file.path, f"update {file_name}", content, file.sha)

    def push_code(self, repo_name, file_name, code):
        self.create_file(repo_name, file_name, code)

if __name__ == "__main__":
    github_token = "your_github_token_here"
    gitgpt = GitGPT(github_token)

    if gitgpt.authenticate():
        # Example usage
        gitgpt.create_repository("NewRepo")
        gitgpt.create_file("NewRepo", "new_file.txt", "Hello, world!")
        gitgpt.edit_file("NewRepo", "new_file.txt", "Hello, GitGPT!")
        gitgpt.push_code("NewRepo", "code.py", "print('Hello from GitGPT')")
    else:
        print("Please check your GitHub token and try again.")
