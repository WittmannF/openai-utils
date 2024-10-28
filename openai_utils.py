from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()


class OpenAIChatClient:
    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY"), model: str = "gpt-4o-mini", system_prompt: str = "", tools: list = [], max_recursion_count=10, tool_function_map=None, max_tool_calls=10):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.max_recursion_count = max_recursion_count
        self.tool_function_map = tool_function_map or {}
        self.max_tool_calls = max_tool_calls

    def create_chat_completion(self, messages: list, recursion_count=0, additional_system_prompt_context: str = ""):
        # Check if the recursion limit has been reached
        if recursion_count >= self.max_recursion_count:
            return {"error": "Max recursion count reached"}

        # Increment the recursion counter
        recursion_count += 1

        # Prepend the system prompt to the messages if provided
        if self.system_prompt:
            if additional_system_prompt_context:
                system_prompt = self.system_prompt + "\n\n" + additional_system_prompt_context
            else:
                system_prompt = self.system_prompt
            messages.insert(0, {
                "role": "system",
                "content": system_prompt,
            })

        if self.tools:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                tools=self.tools
            )

            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                # Check if the number of tool calls exceeds the max_tool_calls limit
                if len(tool_calls) > self.max_tool_calls:
                    raise ValueError(f"Number of tool calls ({len(tool_calls)}) exceeds the maximum allowed ({self.max_tool_calls}).")

                response_message = response.choices[0].message.model_dump()
                messages.append(response_message)
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name

                    if tool_name in self.tool_function_map:
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Call the appropriate function based on the tool name
                        tool_response = self.tool_function_map[tool_name](**arguments)
                        
                        function_call_result_message = {
                            "role": "tool",
                            "content": json.dumps(tool_response),
                            "tool_call_id": tool_call.id  # Ensure the correct tool_call_id is used
                        }
                        messages.append(function_call_result_message)
                return self.create_chat_completion(messages, recursion_count)
            return response

        else:
            return self.client.chat.completions.create(
                messages=messages,
                model=self.model,
            )

    def chat(self, message: str, additional_system_prompt_context: str = "", image_url: str = None):
        """Chat with a single message string."""
        try:
            message_content = message
            if image_url:
                message_content = [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]

            single_message_response = self.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ],
                additional_system_prompt_context=additional_system_prompt_context            )
            single_message_response = single_message_response.choices[0].message.content
            return single_message_response
        except Exception as e:
            return f"The following error occurred: {e}"