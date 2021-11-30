from . import Response

class GetBar(Response):
    content_layout = [str, float, float, float, float, int]

    def time(self) -> str:
        return self[0]

    def open(self) -> float:
        return self[1]

    def high(self) -> float:
        return self[2]

    def low(self) -> float:
        return self[3]

    def close(self) -> float:
        return self[4]

    def volume(self) -> int:
        return self[5]