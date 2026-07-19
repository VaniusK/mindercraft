from imports import *
import inspect

def format_response(response: str) -> str:
    if len(response) > 0:
        if response[0] == response[-2] == '"':
            response = response[1:-2]
    return response

def functions_to_json(functions: list[Callable]) -> list[dict[Any, Any]]:
    type_mapper = {
        "int": "number",
        "str": "string"
    }
    jsons = []
    for function in functions:
        json = {}
        json["type"] = "function"
        json["function"] = {}
        json["function"]["name"] = function.__name__
        json["function"]["description"] = function.__doc__
        json_params = {}
        json_params["type"] = "object"
        function_params = {}
        required_params = []
        sig = inspect.signature(function)
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            function_params[name] = {
                "type": type_mapper[param.annotation.__name__]
            }
            if param.default == inspect.Parameter.empty:
                required_params.append(name)
        
        json_params["properties"] = function_params;
        json_params["required"] = required_params;
        json["function"]["parameters"] = json_params
        jsons.append(json)
    return jsons


class BaseLLM(ABC):
    """
       Абстрактный базовый класс для всех LLM.
       Определяет общий интерфейс.
       """

    def __init__(self, api_key : str, model : str, agent_functions : List[Callable],  **kwargs):
        """
        Инициализация LLM.

        Args:
            api_key: Ключ API.
            model: Название модели.
            agent_functions: Функции, которые может вызывать агент
            **kwargs:  Дополнительные параметры, специфичные для конкретной LLM.
        """
        self.api_key = api_key
        self.model = model
        self.agent_functions = agent_functions
        self.extra_args = kwargs

    @abstractmethod
    def send_message(self, history: List[Dict[Any, Any]]) -> str:
        """
        Отправляет сообщение в LLM и возвращает ответ.

        Args:
            history: История сообщений. Зависит от используемой LLM, но обычно поддерживает
                текст, изображения и документы
        Returns:
            Текст ответа от LLM.
        """
        pass
