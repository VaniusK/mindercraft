from imports import *
from config import config
from minecraft_agent import MinecraftAgent
from llm import LLM

def main():
    # Создаем экземпляр MinecraftAgent
    agents = [MinecraftAgent(
        config["MINECRAFT_HOST"],
        config["MINECRAFT_PORT"],
        config["MINECRAFT_VERSION"],
        config["MINECRAFT_USERNAME"] + (str(i + 1) if i > 0 else "")
    ) for i in range(1)]



    # Запускаем бота
    for agent in agents:
        agent.start()

    while True:
        pass




if __name__ == "__main__":
    main()