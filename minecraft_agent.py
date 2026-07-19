from imports import *
from llm import LLM
from context_handler import ContextHandler
from function_handler import FunctionHandler


class MinecraftAgent:
    def __init__(self, host: str, port: int, version: str, username: str):
        self.host = host
        self.port = port
        self.version = version
        self.ws = None
        self.loop = asyncio.new_event_loop()
        self.process = None
        self.to_answer = threading.Event()
        self.delay = 0.1
        self.pending_results = {}
        self.context_handler = ContextHandler(username, config["character"])
        self.function_handler = FunctionHandler(self.context_handler, self.send_command, self.pending_results)
        self.llm = LLM(None, self.function_handler.functions)

    async def connect_websocket(self):
        """Устанавливает соединение с WebSocket-сервером."""
        while True:
            try:
                async with websockets.connect("ws://localhost:3000") as ws:
                    self.ws = ws
                    print("Подключились к сокету")
                    async for message in ws:
                        print(message)
                        data = json.loads(message)
                        match data["type"]:
                            case "chat":
                                self.context_handler.add_event(data)
                                if data['sender'] != self.context_handler.username:
                                    self.to_answer.set()
                            case "result":
                                self.context_handler.add_event(data)
                                self.pending_results[data["id"]].set()
                            case "inventory":
                                self.context_handler.update_inventory(data["content"])
            except Exception as e:
                print(f"Ошибка сокета {e}")
                await asyncio.sleep(2)

    def run_websocket(self):
        """Запускает asyncio event loop в отдельном потоке."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_websocket())

    def start(self):
        """Запускает бота Mineflayer"""
        command = [
            os.path.expanduser("~/.nvm/versions/node/v24.18.0/bin/node"),
            "mineflayer_bot.js",
            "--host", self.host,
            "--port", str(self.port),
            "--version", self.version,
            "--username", self.context_handler.username,
        ]

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        time.sleep(3)
        threading.Thread(target=self.run_websocket, daemon=True).start()
        threading.Thread(target=self.main_loop, daemon=True).start()

    def send_command(self, command: dict):
        """Отправляет команду через WebSocket."""
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send(json.dumps(command)), self.loop)

    def stop(self):
        """Останавливает бота Mineflayer."""
        if self.process:
            self.ws.close()
            self.process.terminate()
            self.process.wait()
            self.process = None

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def main_loop(self):
        while True:
            prompt = self.context_handler.get_prompt()
            if "STOP" in prompt[-1]['content']:
                break
            self.to_answer.wait()
            self.to_answer.clear()
            time.sleep(0.5)
            prompt = self.context_handler.get_prompt()
            self.llm.send_message(prompt)

        self.stop()
