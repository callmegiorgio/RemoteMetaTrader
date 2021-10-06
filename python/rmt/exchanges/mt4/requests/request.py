from rmt import error
from ..  import Content

class Request:
    command = ''

    def content(self) -> Content:
        raise error.NotImplementedException(self.__class__, 'content')