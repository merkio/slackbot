from slackbot.tests.base import Base
from slackbot import *


class TestBot(Base):

    def test_slack_connect(self, bot):
        assert True == bot.slack_connect()

    def test_slack_read_rtm(self, bot):
        bot.slack_connect()
        print(bot.read_rtm())

    def test_parse_message(self, bot):
        assert self.input_parse == bot.parse_slack_input(self.input)

    def test_get_bot_id(self, bot):
        assert bot.get_bot_id(BOT_NAME) == BOT_ID

    def test_send_message(self, bot):
        assert bot.send_message('DHWA8M8NN', 'Testing writing to slack')
