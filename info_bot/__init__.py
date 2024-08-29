import os
import json
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI
from info_bot.tools.tools import Search,BookInformation
from info_bot.tools.tools_kit import ToolKit
from info_bot.logger import logger

_CLIENT = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
class Agent:
    def __init__(self, tool_kit: ToolKit):
        self.tool_kit = tool_kit
        logger.info("Agent initialized")

    def run(self, user_query: str):
        logger.debug(f'{user_query = }')
        system_prompt = f"""You are a helpful ai assistant.
        You only have access to below tools, and think and select one of these tools tools to assist user.
        
        === Tools ===:
        {"\n".join(self.tool_kit)}

        === Json schema ===
        Respond in below json schema
        {{"tool_name": "select one tool available","tool_input": "input to tool response must be schema in tool description"}}
        """
        logger.info("Waiting for agent to select a tool")
        completion = _CLIENT.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role" : "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        )
        tool_selected = completion.choices[0].message.content
        logger.info(f"tool selected = {tool_selected}")
        return self.tool_kit.run(tool_selected)
    

def main(user_query,op):
    print(user_query)
    tool_kit = ToolKit([Search(name = "search_tool"),BookInformation(tool_name= "book_store")])
    agent = Agent(tool_kit = tool_kit)
    result = agent.run(user_query)
    if op is not None:
        with open(op,'w') as f: json.dump(result,f)
        print(f'\033[38;5;2mOutput written to {op} file\033[0m')
    else:
        print(result['reply'])

if __name__ == '__main__':
    main(input(f"User query: ").strip())
