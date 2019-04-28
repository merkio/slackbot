import pytest
from slackbot import *
from slackbot.handlers import Message


class Base:
    input = [{'client_msg_id': 'eddb99f5-ead0-47e3-8fb2-0e237a990491', 'suppress_notification': False,
              'type': 'message', 'text': '<@UHW8P82SX> Wh', 'user': 'UJ7NNK2L8', 'team': 'TJ7NNK1HN',
              'channel': 'DHWA8M8NN', 'event_ts': '1556392996.001000', 'ts': '1556392996.001000'}]

    input_parse = Message('<@UHW8P82SX>', 'Wh', 'DHWA8M8NN')

    @pytest.fixture
    def bot(self):
        handler = EchoHandler()
        handler.set_next(InvalidInputHandler())
        return SlackBot(handler)
