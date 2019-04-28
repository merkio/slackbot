from slackbot.tests.base import Base
from slackbot import Message, BOT_ID, SlackBot


class TestEcho(Base):

    def test_echo_handler(self, bot: SlackBot):
        assert bot.handle_message(Message(BOT_ID, 'Echo handler test', 'DHWA8M8NN'))\
                   .get('message').get('text') == 'Echo handler test'
