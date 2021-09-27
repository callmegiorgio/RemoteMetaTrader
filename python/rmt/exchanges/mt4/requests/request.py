import json
from typing import Dict

class Request:
    command = ''

    def message(self) -> Dict:
        return {}

    def serialize(self) -> str:
        cmd = self.command

        if cmd == '':
            raise ValueError('command is empty')

        msg = self.message()

        if not isinstance(msg, Dict):
            raise ValueError('error: message must be a dict')

        obj = {
            'cmd': cmd,
            'msg': msg
        }

        return json.dumps(obj)