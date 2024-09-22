import os

VERSION = "0.1.0"
APPLICATION_NAME = 'sixgpt'

SIXGPT_TMP_DIR = os.path.expanduser("~/.sixgpt")

TMP_MINER_LOG = f"{SIXGPT_TMP_DIR}/miner.log"
TMP_PID_FILE = f"{SIXGPT_TMP_DIR}/miner.pid"
TMP_TWITTER_AUTH = f"{SIXGPT_TMP_DIR}/twitter.cookies"
TMP_DRIVE_AUTH = f"{SIXGPT_TMP_DIR}/drive.token"
TMP_VOLARA_TOKEN = f"{SIXGPT_TMP_DIR}/volara.jwt"
TMP_OPENAI_TOKEN = f"{SIXGPT_TMP_DIR}/openai.token"

TIMELINE_SLEEP_INTERVAL = 1
ERROR_SLEEP_INTERVAL = 15
TARGET_EXAMPLE_COUNT = 5

NETWORK = "satori"
SIXGPT_API = "https://api.sixgpt.xyz/v1-sixgpt"

DLP_ADDRESS = "0x31Aa4c1945207566cD804067219b184B55E35aa7"
MODEL_NAME = "gpt-4o"

VANA_HOTKEY = os.getenv("VANA_HOTKEY", "default")
VANA_COLDKEY = os.getenv("VANA_COLDKEY", "default")