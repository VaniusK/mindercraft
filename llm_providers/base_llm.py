from imports import *
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