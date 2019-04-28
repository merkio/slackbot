from slackbot.tests.base import Base
from slackbot import Message, BOT_ID, SlackBot


class TestEcho(Base):

    def test_invalid_handler(self, bot: SlackBot):
        assert bot.handle_message(Message(BOT_ID, '', 'DHWA8M8NN'))\
                   .get('message').get('text') == 'Invalid command'
