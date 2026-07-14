import queue
from context_handler import ContextHandler
from typing import Callable

class FunctionHandler:
    def __init__(self, context_handler, send_command: Callable):
        self.functions = [self.send_chat, self.go_to_player]
        self.context_handler = context_handler
        self.send_command = send_command

    def send_chat(self, message: str) -> None:
        """Отправляет сообщение в чат от лица агента"""
        print("Called send_chat()")
        self.context_handler.add_event({ "type": "chat", "sender": self.context_handler.username, "role": "assistant", "content": self.context_handler.username + " sent chat message: \"" + message + "\"" })
        command = {"type": "chat", "message": message}
        self.send_command(command)

    def go_to_player(self, player_name: str) -> None:
        """Идет к игроку, пока расстояние до него не будет <= 3 блока.
        Возвращает success, если успешно дошёл и стоит около игрока
        Возвращает error, если не смог дойти.
        """
        print("Called go_to_player()")
        command = {"type": "go_to_player", "player_name": player_name, "distance": 3}
        self.context_handler.add_event({"role": "tool", "content": "executed command " + str(command)})
        self.send_command(command)
