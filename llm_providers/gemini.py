from imports import *
from llm_providers.base_llm import BaseLLM

class Gemini(BaseLLM):
    def __init__(self, api_key : str, model : str, agent_functions : List[Callable], **kwargs):
        super().__init__(api_key, model, agent_functions, **kwargs)
        self.client = genai.Client(api_key=self.api_key, ) # Устанавливаем ключ API
        self.config = types.GenerateContentConfig(
            tools=agent_functions,
            max_output_tokens=1000,
            top_k=64,
            top_p=0.95,
            temperature=1.5
        )
        self.model = model



    def send_message(self, history: List[Dict[Any, Any]]) -> str:
        try:


            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=str(history),
                config=self.config
            )
            return response.text

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"

