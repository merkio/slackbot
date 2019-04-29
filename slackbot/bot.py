import logging.config
import logging
from os import path

from slackclient import SlackClient

from slackbot import *

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'config', 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)


class SlackBot:
    def __init__(self, handler: Handler) -> None:
        self.slack_client = SlackClient(config.bot_token)
        self.bot_id = config.bot_id
        self.bot_at_id = '<@{}>'.format(self.bot_id)
        self.handler = handler

    def slack_connect(self):
        return self.slack_client.rtm_connect()

    def parse_slack_input(self, inputs):
        for input in inputs:
            if input.get('type') == 'message':
                logger.debug('Get input {}'.format(str(input).replace("'", '"')))
                command_to_bot = input.get('text').split(self.bot_at_id)
                if len(command_to_bot) > 1:
                    message = Message(bot_id=self.bot_at_id, text=command_to_bot[1].strip(' '),
                                      channel=input.get('channel'))
                    return message

    def handle_message(self, message: Message):
        if message:
            return self.handler.handle(message, self)

    def send_message(self, channel: str, text: str):
        logger.debug('Send message: {} to channel: {}'.format(str(text).replace("'", '"'), str(channel).replace("'", '"')))
        return self.slack_client.api_call('chat.postMessage', channel=channel, text=text, as_user=True)

    def read_rtm(self):
        return self.slack_client.rtm_read()

    def get_bot_id(self, bot_name):
        users = self.slack_client.api_call('users.list').get('members', [])
        for user in users:
            if bot_name in user.get('name', '') and not user.get('deleted'):
                return user.get('id')
