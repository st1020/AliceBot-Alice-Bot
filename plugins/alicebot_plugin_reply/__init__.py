import re
import json

from plugins.alicebot_plugin_public import BasePlugin

from .config import Config


class Reply(BasePlugin[Config]):
    priority: int = 1
    plugin_config_class: Config = Config

    def __post_init__(self):
        with open(self.plugin_config.data_file, 'r') as fp:
            if self.plugin_config.data_type == 'json':
                json_data = json.load(fp)
            else:
                raise ValueError(f'data_type must be json, not {self.plugin_config.data_type}')
        self.rule_to_message = {
            item['rule']: item['message']
            for item in json_data if isinstance(item, dict) and 'rule' in item.keys() and 'message' in item.keys()
        }

    async def handle(self) -> None:
        msg = self.rule_to_message[self.msg_match.re.pattern]
        if isinstance(msg, str):
            await self.event.reply(self.format_str(msg, self.msg_match.string))
        else:
            await self.event.reply(msg)

    def str_match(self, msg_str: str) -> bool:
        msg_str = msg_str.strip()
        for rule in self.rule_to_message.keys():
            msg_match = re.fullmatch(rule, msg_str, flags=re.I if self.plugin_config.ignore_case else 0)
            if msg_match:
                self.msg_match = msg_match
                return bool(self.msg_match)
        return False