from abc import ABC, abstractmethod

class SDKAuthenticate(ABC):
    def __init__(self):
        super().__init__()
        self._token_map = {}

    @abstractmethod
    def get_token(self, username, password, proxy=None):
        pass

    @abstractmethod
    def get_refresh_token(self, refresh_token, proxy=None):
        pass
