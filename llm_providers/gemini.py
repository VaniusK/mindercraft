from imports import *
from llm_providers.base_llm import *

# NOT SUPPORTED
# Use Custom + gemini's openai-compatible API


class Gemini(BaseLLM):
    def __init__(self, api_key : str, model : str, agent_functions : List[Callable], **kwargs):
        super().__init__(api_key, model, agent_functions, **kwargs)
        self.client = genai.Client(api_key=self.api_key, )
        self.config = types.GenerateContentConfig(
            #tools=agent_functions,
            max_output_tokens=1000,
            thinking_config = types.ThinkingConfig(
            thinking_level="LOW"
            )
        )
        self.model = model

    def send_message(self, history: List[Dict[Any, Any]]) -> str:
        response = self.client.models.generate_content(
                model=self.model,
                contents=str(history),
                config=self.config
            )
        return format_response(response.text)

