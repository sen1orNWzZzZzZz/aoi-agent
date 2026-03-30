import os
from pathlib import Path
from core.config_loader import getConfig

cfg = getConfig()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = Path(
      os.getenv("FILE_AGENT_WORKSPACE", cfg["app"]["workspace_root"])
  ).resolve()


API_KEY = (
    cfg['model']['api_key']
)
BASE_URL = cfg['model']['base_url']
MODEL_NAME = cfg['model']['model_name']

MAX_LOOP = cfg['app']['max_loop']
MAX_FILE_CHARS = cfg['app']['max_file_chars']

api_key = API_KEY
base_url = BASE_URL
model = MODEL_NAME
