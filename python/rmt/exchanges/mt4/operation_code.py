from enum import IntEnum

class OperationCode(IntEnum):
    BUY        = 0
    SELL       = 1
    BUY_LIMIT  = 2
    SELL_LIMIT = 3
    BUY_STOP   = 4
    SELL_STOP  = 5