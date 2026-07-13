from llm_providers.base_llm import *
from openai import OpenAI


class Custom(BaseLLM):
    def __init__(self, api_key : str, model : str, agent_functions : List[Callable], **kwargs):
        super().__init__(api_key, model, agent_functions, **kwargs)
        self.client = OpenAI(api_key=self.api_key, base_url=kwargs["base_url"]
)
        self.model = model
        self.agent_functions = agent_functions
        self.agent_functions_json = functions_to_json(agent_functions)
        self.functions_dict = {func.__name__: func for func in self.agent_functions}

    def send_message(self, history: List[Dict[Any, Any]]) -> str:
        response = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                reasoning_effort="minimal",
                tools=self.agent_functions_json
            )
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_to_call = self.functions_dict[function_name]
                function_to_call(**function_args)

        return format_response(response.choices[0].message.content or "") 

