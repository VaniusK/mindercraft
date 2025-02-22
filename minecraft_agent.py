from imports import *
from llm import LLM


class MinecraftAgent:
    def __init__(self, host: str, port: int, version: str, username: str):
        self.host = host
        self.port = port
        self.version = version
        self.username = username
        self.ws = None
        self.loop = asyncio.new_event_loop()
        self.process = None
        self.chat_log = []
        self.chat_log_lock = threading.Lock()
        self.to_answer = threading.Event()
        self.result_queue = queue.Queue()
        self.chat_updated = threading.Event()
        self.delay = 0.1
        self.llm = LLM('gemini', [self.go_to_player])

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
                        with self.chat_log_lock:
                            self.chat_log.append(data)

                        if data["type"] == "chat":
                            if data['role'] != self.username:
                                self.to_answer.set()
                        else:
                            self.result_queue.put(data)
                        self.chat_updated.set()
            except Exception as e:
                print(f"Ошибка сокета {e}")
                time.sleep(2)  # Реконнект через 2 секунды

    def run_websocket(self):
        """Запускает asyncio event loop в отдельном потоке."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_websocket())

    def start(self):
        """Запускает бота Mineflayer"""
        command = [
            "C:\\nvm4w\\nodejs\\node.exe",
            "mineflayer_bot.js",
            "--host", self.host,
            "--port", str(self.port),
            "--version", self.version,
            "--username", self.username,
        ]

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        time.sleep(5)
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

    def send_chat(self, message: str) -> None:
        """Отправляет сообщение в чат от лица агента"""
        if self.process and self.process.poll() is None:
            command = {"type": "chat", "message": message}
            self.send_command(command)

    def go_to_player(self, player_name: str) -> dict:
        """Идет к игроку, пока расстояние до него не будет <= 3 блока.
        Возвращает success, если успешно дошёл и стоит около игрока
        Возвращает error, если не смог дойти.
        """
        if self.process and self.process.poll() is None:
            command = {"type": "go_to_player", "player_name": player_name, "distance": 3}
            print("Going")
            with self.chat_log_lock:
                self.chat_log.append(command)
            self.send_command(command)

            try:
                return self.result_queue.get()
            except queue.Empty:
                return False
        return False

    def get_chat_log(self):
        with self.chat_log_lock:
            return self.chat_log.copy()

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def main_loop(self):
        while True:
            log = self.get_chat_log()
            if len(log) > 0 and 'content' in log[-1] and log[-1]['content'] == 'stop':
                break
            if self.to_answer.is_set():
                self.to_answer.clear()
                time.sleep(0.5)
                log = self.get_chat_log()
                print(log)
                response = self.llm.send_message(log + config['prompt'])
                if response:
                    self.send_chat(response)

        self.stop()
