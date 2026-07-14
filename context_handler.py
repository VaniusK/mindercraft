from typing import Any
import threading

class ContextHandler:
    def __init__(self, system_prompt: list[dict[Any, Any]], username: str):
        self.system_prompt = system_prompt
        self.events: list[dict[Any, Any]] = []
        self.events_lock = threading.Lock()
        self.username = username
    
    def add_event(self, event: dict[Any, Any]):
        if "role" not in event:
            raise Exception(str(event) + " doesn't contain role field")
        if event["role"] not in ["user", "system", "assistant", "tool"]:
            raise Exception("role " + event["role"] + " is not supported")
        if "content" not in event:
            raise Exception(str(event) + " doesn't contain content field")
        with self.events_lock:
            self.events.append({"role": event["role"], "content": event["content"]})
    
    def get_prompt(self):
        return self.events + self.system_prompt
