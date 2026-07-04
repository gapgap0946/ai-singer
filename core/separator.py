"""人声/伴奏分离模块，基于 Demucs。"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from core import config


class SeparationError(RuntimeError):
    pass


def separate(input_audio: str | Path, work_dir: str | Path | None = None) -> dict[str, Path]:
    """将输入音频分离为人声与伴奏。

    返回包含 ``vocals`` 与 ``accompaniment`` 两个键的字典，值为输出 wav 路径。
    """
    input_audio = Path(input_audio)
    if not input_audio.exists():
        raise SeparationError(f"输入音频不存在: {input_audio}")

    work_dir = Path(work_dir) if work_dir else config.WORK_DIR
    work_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs",
        "-n", config.DEMUCS_MODEL,
        "--two-stems", "vocals",
        "-o", str(work_dir),
        str(input_audio),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SeparationError(f"Demucs 分离失败:\n{proc.stderr}")

    stem_dir = work_dir / config.DEMUCS_MODEL / input_audio.stem
    vocals = stem_dir / "vocals.wav"
    accompaniment = stem_dir / "no_vocals.wav"

    if not vocals.exists() or not accompaniment.exists():
        raise SeparationError(f"未找到分离结果，检查目录: {stem_dir}")

    return {"vocals": vocals, "accompaniment": accompaniment}
