import json
from info_bot.logger import logger
from info_bot.tools.tools import Tool

class ToolKit:
    def __init__(self, tools: list[Tool]):

        self.tools = {tool.name: tool for tool in tools}

        logger.info("ToolKit initialized")
        logger.debug(f'{self.tools = }')

    def __iter__(self):
        logger.info("Toolkit is noe oterabel")
        res = [tool.description for tool in self.tools.values()]
        logger.debug(f'{res = !r}, {res.__class__}')
        return iter(res)
    
    def run(self, json_object):
        logger.debug(f"Response after tool selection = {json_object!r}")
        dct = json.loads(json_object)
        return self.tools[dct['tool_name']].run(dct["tool_input"])