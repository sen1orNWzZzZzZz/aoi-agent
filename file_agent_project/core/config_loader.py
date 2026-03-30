import yaml
from pathlib import Path

# 获取当前文件(config_loader.py)的绝对路径
# 然后取上级目录(core的父目录 = 项目根目录)，再找 config.yaml
config_path = Path(__file__).resolve().parent.parent / "config.yaml"

# print(f"查找路径: {config_path}")  # 调试用，确认路径正确

def getConfig():
    with open(config_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data