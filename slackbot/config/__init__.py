from slackbot.config.config import *

config = eval('{}()'.format(os.getenv('ENVIRONMENT', 'development').capitalize()))
