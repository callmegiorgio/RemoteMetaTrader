from typing  import Dict, Callable, Tuple, Type
from ..      import Content
from .       import Event

class Dispatcher:
    """Delivers the content of an event message to an event handler."""

    def __init__(self):
        self._event_data: Dict[str, Tuple[Event, Content]] = {}

    def register(self, static_name: str, event_type: Type[Event], handler: Callable[[Event], None]):
        if not static_name.isalpha():
            raise ValueError("expected alphabetic static part of event name (got: '{}')".format(static_name))

        self._event_data[static_name] = (event_type, handler)

    def dispatch(self, event_name: str, content: Content):
        static_name  = None
        dynamic_name = None
        dynamic_name_index = event_name.find('.')

        if dynamic_name_index != -1:
            static_name  = event_name[0:dynamic_name_index]
            dynamic_name = event_name[(dynamic_name_index + 1):]

            if dynamic_name == '':
                raise ValueError(
                    "received event message with static name '{}' and empty dynamic name"
                    .format(static_name)
                )
        else:
            static_name = event_name
            dynamic_name = ''

        if static_name not in self._event_data:
            raise ValueError("received event message with unknown name '%s'" % static_name)
        
        EventType, handler = self._event_data[static_name]
        
        event = EventType(dynamic_name, content)

        handler(event)