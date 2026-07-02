import json
import os
from datetime import datetime

FILE = "config.json"


# =========================
# 讀取設定（安全版）
# =========================
def load_config():
    if not os.path.exists(FILE):
        return {"my_routes": []}

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 防呆：避免舊版本
        if "my_routes" not in data:
            data["my_routes"] = []

        return data

    except:
        return {"my_routes": []}


# =========================
# 儲存設定（防覆蓋 + 防壞檔）
# =========================
def save_config(data):
    tmp_file = FILE + ".tmp"

    # 先寫 temp，避免寫壞檔
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(tmp_file, FILE)


# =========================
# 初始化船舶資料
# =========================
def init_ship(config, vessel_code):
    if vessel_code not in config:
        config[vessel_code] = {
            "routes": [],
            "updated_at": None
        }
    return config


# =========================
# 更新時間戳
# =========================
def touch(config, vessel_code):
    config[vessel_code]["updated_at"] = datetime.now().isoformat()
    return config