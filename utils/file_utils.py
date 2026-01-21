import json
import os
import shutil
from utils.logger import get_logger

def load_json(path, default):
    logger = get_logger()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Falha ao carregar %s: %s", path, e)
        return default

def save_json(path, data):
    logger = get_logger()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        if os.path.exists(path):
            shutil.copy2(path, f"{path}.bak")
        os.replace(tmp_path, path)
    except OSError as e:
        logger.error("Falha ao salvar %s: %s", path, e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
