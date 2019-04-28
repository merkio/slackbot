from slackbot import SlackBot, EchoHandler, InvalidInputHandler
import time


if __name__ == '__main__':
    handler = EchoHandler()
    handler.set_next(InvalidInputHandler())
    bot = SlackBot(handler)
    bot.slack_connect()
    while True:
        bot.handle_message(bot.parse_slack_input(bot.read_rtm()))
        time.sleep(1)
