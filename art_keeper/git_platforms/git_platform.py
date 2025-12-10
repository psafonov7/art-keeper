from abc import ABC, abstractmethod


class GitPlatform(ABC):
    @abstractmethod
    async def prepare_repo(self, repo_path: str):
        raise ValueError("Must be overriden")
