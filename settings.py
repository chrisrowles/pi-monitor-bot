from dotenv import load_dotenv
import os
from os.path import dirname, join

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

URL = str(os.environ.get('SYSAPI_URL'))
TOKEN = str(os.environ.get('DISCORD_TOKEN'))
USER_ID= str(os.environ.get('USER_ID'))
CHANNEL_ID= int(os.environ.get('CHANNEL_ID'))
