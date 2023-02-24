import os
from pathlib import Path

LOCAL_PROJECT_PATH = os.path.expanduser("~\\.gxiba\\")
LOCAL_PROJECT_TEMP_PATH = os.path.expanduser("~\\.gxiba\\temp\\")
LOCAL_PROJECT_LOG_PATH = os.path.expanduser("~\\.gxiba\\logs\\")
LOCAL_PROJECT_CONFIG_PATH = os.path.expanduser("~\\.gxiba\\config.json")

if not os.path.exists(LOCAL_PROJECT_TEMP_PATH):
    Path(LOCAL_PROJECT_TEMP_PATH).mkdir(parents=True, exist_ok=True)
    Path(LOCAL_PROJECT_LOG_PATH).mkdir(parents=True, exist_ok=True)
