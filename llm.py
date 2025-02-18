from imports import *
class LLM:
    def __init__(self, llm_name : str, agent_functions : List[Callable]):
        self.agent_functions = agent_functions
        self.llm = self.get_llm(llm_name)


    def get_llm(self, llm_name=None):
        """
        Фабричный метод для создания экземпляров LLM на основе конфигурации.
        """
        if llm_name is None:
            llm_name = config["default_llm"]

        llm_config = config["llms"].get(llm_name)
        if not llm_config:
            raise ValueError(f"LLM '{llm_name}' not found in config.")

        module_name = llm_config["module"]
        class_name = llm_config["class"]

        try:
            # Динамически импортируем модуль
            module = importlib.import_module(module_name)
            # Получаем класс из модуля
            llm_class = getattr(module, class_name)
            # Создаем экземпляр класса, передавая параметры из конфига
            llm_instance = llm_class(**llm_config, agent_functions=self.agent_functions)
            return llm_instance
        except ImportError:
            raise ImportError(f"Could not import module '{module_name}'.")
        except AttributeError:
            raise AttributeError(f"Class '{class_name}' not found in module '{module_name}'.")
        except Exception as e: # Обрабатываем другие исключения
             raise Exception(f"An error occurred while creating LLM instance: {e}")

    def send_message(self, history : List[Dict[Any, Any]]) -> str:
        return self.llm.send_message(history)