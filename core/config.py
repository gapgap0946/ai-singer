from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
RVC_MODELS_DIR = MODELS_DIR / "rvc"
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "outputs" / "uploads"
WORK_DIR = BASE_DIR / "outputs" / "work"

for _d in (MODELS_DIR, RVC_MODELS_DIR, OUTPUTS_DIR, UPLOADS_DIR, WORK_DIR):
    _d.mkdir(parents=True, exist_ok=True)

DEMUCS_MODEL = "htdemucs"

DEFAULT_PITCH = 0
DEFAULT_INDEX_RATE = 0.75
DEFAULT_F0_METHOD = "rmvpe"

DEVICE = "cuda:0"

API_HOST = "0.0.0.0"
API_PORT = 8000

SUPPORTED_AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
