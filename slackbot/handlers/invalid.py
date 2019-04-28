from slackbot.handlers.abstract_handler import Handler, Message


class InvalidInputHandler(Handler):

    def handle(self, message: Message, bot):
        return bot.send_message(channel=message.channel, text='Invalid command')
