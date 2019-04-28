from slackbot.handlers.abstract_handler import Handler, Message


class EchoHandler(Handler):

    def handle(self, message: Message, bot):
        if message.text:
            return bot.send_message(message.channel, message.text)
        else:
            return self._next_handler.handle(message, bot)
