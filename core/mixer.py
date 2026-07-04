"""混音后处理模块：将转换后人声与伴奏合成成品。"""
from __future__ import annotations

from pathlib import Path

from core import config


class MixError(RuntimeError):
    pass


def mix(
    vocals_path: str | Path,
    accompaniment_path: str | Path,
    output_path: str | Path,
    vocal_gain_db: float = 0.0,
    accompaniment_gain_db: float = 0.0,
) -> Path:
    """将人声与伴奏叠加混音，导出为成品音频。"""
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise MixError("未安装 pydub，请先执行 pip install pydub") from e

    vocals_path = Path(vocals_path)
    accompaniment_path = Path(accompaniment_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vocals = AudioSegment.from_file(vocals_path)
    accompaniment = AudioSegment.from_file(accompaniment_path)

    if vocal_gain_db:
        vocals = vocals.apply_gain(vocal_gain_db)
    if accompaniment_gain_db:
        accompaniment = accompaniment.apply_gain(accompaniment_gain_db)

    mixed = accompaniment.overlay(vocals)

    fmt = output_path.suffix.lstrip(".").lower() or "wav"
    mixed.export(output_path, format=fmt)

    if not output_path.exists():
        raise MixError(f"混音未生成输出文件: {output_path}")
    return output_path
