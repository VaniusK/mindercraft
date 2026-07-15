from typing import Any
import threading
from jinja2 import Environment, FileSystemLoader

class ContextHandler:
    def __init__(self, username: str, character: str):
        self.events: list[dict[Any, Any]] = []
        self.events_lock = threading.Lock()
        self.username = username
        env = Environment(loader=FileSystemLoader('prompts'))
        self.template = env.get_template(f'characters/{character}.jinja2')
        self.inventory = ""
    
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
        result = self.template.render(username=self.username, inventory=self.inventory)
        self.system_prompt = {"role": "system", "content": result}
        return self.events + [self.system_prompt]
    
    def update_inventory(self, inventory):
        for i in range(len(inventory)):
            inventory[i] = {"name": inventory[i]["name"], "type": inventory[i]["type"], "count": inventory[i]["count"]}
        self.inventory = inventory
