from datetime import datetime


class Logger:
    def __init__(self) -> None:
        self._log = ""
        
    def log(self, msg: str) -> None:
        self._log += f"{datetime.now()} : {msg}\n"
    
    def get_and_clear(self) -> str:
        log = self._log
        self._log = ""
        return log