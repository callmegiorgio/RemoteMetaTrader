# RemoteMetaTrader

## Motivation

[TFW][ref-tfw] you wanna do algorithmic trading on Python, but your broker's only platform is MetaTrader 4.

## About

RemoteMetaTrader is a library that allows making MetaTrader 4 calls remotely from Python. As such, it is both a Python and MQL4 library. The library is inspired by [Darwinex's solution][ref-dwx], with a few differences:
- Command abstraction: your Python application doesn't need to be aware of the underlying messaging protocol.
- Event mechanism: your Python application gets to know the shit that you do on MetaTrader 4 behind its back.
- Classes for trading abstractions: `Bar`, `Order`, `Instrument`, etc.
- Saner Python method names (or maybe it's just my weird preference to have a method called `close_order()` instead of `_DWX_MTX_CLOSE_TRADE_BY_TICKET()`... LOL)

API is still unstable.

## Installation

TODO

## Usage

TODO

[ref-tfw]: <https://www.merriam-webster.com/words-at-play/what-does-tfw-mean-that-feeling-when>
[ref-dwx]: <https://github.com/darwinex/DarwinexLabs/tree/master/tools/dwx_zeromq_connector/v2.0.1>