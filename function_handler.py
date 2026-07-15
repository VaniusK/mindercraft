import queue
from context_handler import ContextHandler
import threading
from typing import Callable
import uuid

class FunctionHandler:
    def __init__(self, context_handler, send_command: Callable, pending_results: dict[str, threading.Event]):
        self.functions = [self.send_chat, self.go_to_player, self.give_item]
        self.context_handler = context_handler
        self.send_command = send_command
        self.pending_results = pending_results

    def send_chat(self, message: str) -> None:
        """
        Отправляет сообщение в чат от лица агента
        """
        print("Called send_chat()")
        id = str(uuid.uuid4())
        self.pending_results[id] = threading.Event()
        self.context_handler.add_event({ "type": "chat", "sender": self.context_handler.username, "role": "assistant", "content": self.context_handler.username + " sent chat message: \"" + message + "\"" })
        command = {"type": "chat", "message": message, "id": id}
        self.send_command(command)
        self.pending_results[id].wait()
        self.pending_results.pop(id)

    def go_to_player(self, player_name: str) -> None:
        """
        Идет к игроку, пока расстояние до него не будет <= 3 блока.
        Возвращает success, если успешно дошёл и стоит около игрока
        Возвращает error, если не смог дойти.
        """
        print("Called go_to_player()")
        id = str(uuid.uuid4())
        self.pending_results[id] = threading.Event()
        command = {"type": "go_to_player", "id": id, "player_name": player_name, "distance": 3}
        self.context_handler.add_event({"role": "tool", "content": "executed command " + str(command)})
        self.send_command(command)
        self.pending_results[id].wait()
        self.pending_results.pop(id)
    
    def give_item(self, player_name: str, item_type: int, count: int) -> None:
        """
        Поворачивается к игроку и кидает в его сторону 
        count предметов типа item_type(айди предмета)
        Рекомендуется использовать после go_to_player()
        Возвращает error, если предметов нет
        """
        print("Called give_item()")
        id = str(uuid.uuid4())
        self.pending_results[id] = threading.Event()
        command = {"type": "give_item", "id": id, "player_name": player_name, "item_type": item_type, "count": count}
        self.context_handler.add_event({"role": "tool", "content": "executed command " + str(command)})
        self.send_command(command)
        self.pending_results[id].wait()
        self.pending_results.pop(id)
