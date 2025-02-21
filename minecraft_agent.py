from imports import *
from llm import LLM

class MinecraftAgent:
    def __init__(self, host : str, port: int, version: str, username: str):
        self.host = host
        self.port = port
        self.version = version
        self.username = username
        self.process = None
        self.chat_log = []
        self.stderr_log = []
        self._stdout_thread = None
        self._stderr_thread = None
        self._stop_event = threading.Event()
        self.to_answer = False
        self.llm = LLM('gemini', [self.goto_player])

    def _read_output(self, stream, log_list, is_chat=False):
        """Читает вывод из потока и добавляет его в соответствующий лог."""
        while not self._stop_event.is_set():
            try:
                line = stream.readline()
                if line:
                    decoded_line = line.strip()
                    print(decoded_line)
                    if is_chat:
                        try:
                            chat_message = json.loads(decoded_line)
                            log_list.append(chat_message)
                            if chat_message['role'] != self.username:
                                self.to_answer = True
                        except json.JSONDecodeError:
                            print(f"Invalid chat message format: {decoded_line}")
                else:
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error reading output: {e}")
                break

    def start(self):
        """Запускает бота Mineflayer и потоки для чтения вывода."""
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

        self.chat_log.clear()
        self.stderr_log.clear()

        self._stdout_thread = threading.Thread(target=self._read_output, args=(self.process.stdout, self.chat_log, True))
        self._stderr_thread = threading.Thread(target=self._read_output, args=(self.process.stderr, self.stderr_log))
        self._stdout_thread.daemon = True
        self._stderr_thread.daemon = True
        self._stdout_thread.start()
        self._stderr_thread.start()
        self.main_loop()


    def stop(self):
        """Останавливает бота Mineflayer и потоки чтения."""
        if self.process:
            self._stop_event.set()
            if self._stdout_thread:
                self._stdout_thread.join(timeout=2)
            if self._stderr_thread:
                self._stderr_thread.join(timeout=2)
            self.process.terminate()
            self.process.wait()
            self.process = None

    def send_chat(self, message : str) -> None:
        """Отправляет сообщение в чат от лица агента"""
        if self.process and self.process.poll() is None:
            command = {"type": "chat", "message": message}
            self.process.stdin.write(json.dumps(command) + "\n")
            self.process.stdin.flush()

    def goto_player(self, player_name: str) -> bool:
        """Идет к игроку, пока расстояние до него не будет <= 3 блока.
            Возвращает True, если успешно вышел и дошёл до цели, иначе False(если не смог дойти)."""
        print("Going")
        if self.process and self.process.poll() is None:
            command = {"type": "go_to_player", "player_name": player_name, "distance": 3}
            self.process.stdin.write(json.dumps(command) + "\n")
            self.process.stdin.flush()


            return True # Заглушка
        return False


    def get_chat_log(self):
        return self.chat_log.copy()

    def get_stderr_log(self):
        return self.stderr_log.copy()

    def clear_logs(self):
        self.chat_log.clear()
        self.stderr_log.clear()

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def main_loop(self):
        while True:
            log = self.get_chat_log()
            if self.to_answer:
                print(log)
                self.to_answer = False
                response = self.llm.send_message(log + config['prompt'])
                if response:
                    self.send_chat(response)

                if log[-1]['content'] == 'stop':
                    break
            #break

        self.stop()
