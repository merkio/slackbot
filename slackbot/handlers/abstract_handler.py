from abc import ABC, abstractmethod
from collections import namedtuple


Message = namedtuple('Message', 'bot_id text channel')


class Handler(ABC):

    def __init__(self) -> None:
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, message: Message, bot):
        pass
