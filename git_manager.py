import git
from datetime import datetime

class GitManager:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)

    def commit_changes(self, file_path, message):
        self.repo.index.add([file_path])
        self.repo.index.commit(f"{message} - {datetime.now().isoformat()}")

    def get_comment_history(self, file_path):
        history = []
        for commit in self.repo.iter_commits(paths=file_path):
            diff = commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE, paths=file_path)
            for d in diff:
                if d.a_blob and d.b_blob:
                    old_comments = self._extract_comments(d.a_blob.data_stream.read().decode('utf-8'))
                    new_comments = self._extract_comments(d.b_blob.data_stream.read().decode('utf-8'))
                    if old_comments != new_comments:
                        history.append({
                            'commit': commit.hexsha,
                            'date': commit.committed_datetime,
                            'old_comments': old_comments,
                            'new_comments': new_comments
                        })
        return history

    def _extract_comments(self, code):
        # Implement comment extraction logic based on the programming language
        # This is a simplified example for Python-style comments
        return [line.strip() for line in code.split('\n') if line.strip().startswith('#')]
