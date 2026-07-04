from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
RVC_MODELS_DIR = MODELS_DIR / "rvc"
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "outputs" / "uploads"
WORK_DIR = BASE_DIR / "outputs" / "work"

for _d in (MODELS_DIR, RVC_MODELS_DIR, OUTPUTS_DIR, UPLOADS_DIR, WORK_DIR):
    _d.mkdir(parents=True, exist_ok=True)

DEMUCS_MODEL = "htdemucs"

# ===== RVC-WebUI 集成配置（方案A：解耦调用外部 RVC-WebUI）=====
# 请把官方 RVC-WebUI 整合包解压后的根目录路径填在这里，或用环境变量 RVC_WEBUI_DIR 覆盖。
# 整合包地址：https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
RVC_WEBUI_DIR = Path(os.environ.get("RVC_WEBUI_DIR", r"D:\AI\RVC-WebUI"))
# 整合包内的 Python 解释器（通常是自带的 runtime\python.exe）
RVC_PYTHON = Path(os.environ.get("RVC_PYTHON", RVC_WEBUI_DIR / "runtime" / "python.exe"))
# 命令行推理脚本（整合包自带 tools/infer_cli.py）
RVC_INFER_CLI = RVC_WEBUI_DIR / "tools" / "infer_cli.py"

DEFAULT_PITCH = 0
DEFAULT_INDEX_RATE = 0.75
DEFAULT_F0_METHOD = "rmvpe"

DEVICE = "cuda:0"

API_HOST = "0.0.0.0"
API_PORT = 8000

SUPPORTED_AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
