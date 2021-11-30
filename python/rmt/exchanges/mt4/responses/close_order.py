from typing import Optional
from .      import Response

class CloseOrder(Response):
    content_layout = {
        'lots':       float,
        'cp':         float,
        'ct':         str,
        'comment':    (str,   ''),
        'commission': float,
        'profit':     float,
        'swap':       float,
        'new_order': ({
            'ticket':     int,
            'lots':       float,
            'magic':      int,
            'comment':    (str, ''),
            'commission': float,
            'profit':     float,
            'swap':       float
        }, None)
    }

    class NewOrder:
        def __init__(self,
                     ticket:       int,
                     lots:         float,
                     magic_number: int,
                     comment:      str,
                     commission:   float,
                     profit:       float,
                     swap:         float
        ):
            self._ticket       = int(ticket)
            self._lots         = float(lots)
            self._magic_number = int(magic_number)
            self._comment      = str(comment)
            self._commission   = float(commission)
            self._profit       = float(profit)
            self._swap         = float(swap)

        def ticket(self) -> int:
            return self._ticket
        
        def lots(self) -> float:
            return self._lots

        def magic_number(self) -> int:
            return self._magic_number
            
        def comment(self) -> str:
            return self._comment
            
        def commission(self) -> float:
            return self._commission
            
        def profit(self) -> float:
            return self._profit
            
        def swap(self) -> float:
            return self._swap

    def lots(self) -> float:
        return self['lots']

    def close_price(self) -> float:
        return self['cp']

    def close_time(self) -> str:
        return self['ct']

    def comment(self) -> str:
        return self['comment']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']

    def new_order(self) -> Optional[NewOrder]:
        new_order = self['new_order']

        if new_order is not None:
            new_order = CloseOrder.NewOrder(
                ticket       = new_order['ticket'],
                lots         = new_order['lots'],
                magic_number = new_order['magic'],
                comment      = new_order['comment'],
                commission   = new_order['commission'],
                profit       = new_order['profit'],
                swap         = new_order['swap']
            )

        return new_order