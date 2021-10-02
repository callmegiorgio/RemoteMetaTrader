from .. import Content

class Request:
    command = ''

    def content(self) -> Content:
        raise NotImplementedError('%s.%s not implemented' % (self.__name__, self.content.__name__))