"""翻唱流水线编排器。

将「人声分离 → 音色转换 → 混音」串成一条流水线，并预留自然语言意图解析接口
（后续可接入 LLM function-calling）。
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core import config, converter, mixer, separator


@dataclass
class CoverRequest:
    input_audio: Path
    model_name: str
    pitch: int = config.DEFAULT_PITCH
    index_rate: float = config.DEFAULT_INDEX_RATE
    f0_method: str = config.DEFAULT_F0_METHOD
    vocal_gain_db: float = 0.0
    accompaniment_gain_db: float = 0.0
    output_name: str | None = None


@dataclass
class CoverResult:
    output_path: Path
    vocals_path: Path
    accompaniment_path: Path
    converted_vocals_path: Path
    steps: list[str] = field(default_factory=list)


ProgressCallback = Callable[[str, float], None]


def run_cover(
    request: CoverRequest,
    progress: ProgressCallback | None = None,
) -> CoverResult:
    """执行完整翻唱流水线。

    progress 回调形如 progress(message, ratio)，ratio 为 0~1 的进度。
    """
    steps: list[str] = []

    def _report(msg: str, ratio: float) -> None:
        steps.append(msg)
        if progress:
            progress(msg, ratio)

    job_id = uuid.uuid4().hex[:8]
    work_dir = config.WORK_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)

    _report("① 正在分离人声与伴奏…", 0.1)
    stems = separator.separate(request.input_audio, work_dir=work_dir)

    _report("② 正在进行音色转换…", 0.4)
    converted_vocals = work_dir / "converted_vocals.wav"
    converter.convert(
        vocals_path=stems["vocals"],
        model_name=request.model_name,
        output_path=converted_vocals,
        pitch=request.pitch,
        index_rate=request.index_rate,
        f0_method=request.f0_method,
    )

    _report("③ 正在混音合成…", 0.8)
    out_name = request.output_name or f"cover_{request.model_name}_{job_id}.wav"
    output_path = config.OUTPUTS_DIR / out_name
    mixer.mix(
        vocals_path=converted_vocals,
        accompaniment_path=stems["accompaniment"],
        output_path=output_path,
        vocal_gain_db=request.vocal_gain_db,
        accompaniment_gain_db=request.accompaniment_gain_db,
    )

    _report("✅ 完成", 1.0)

    return CoverResult(
        output_path=output_path,
        vocals_path=stems["vocals"],
        accompaniment_path=stems["accompaniment"],
        converted_vocals_path=converted_vocals,
        steps=steps,
    )


def parse_intent(text: str) -> dict:
    """极简意图解析占位实现。

    后续可替换为 LLM function-calling：输入自然语言，输出结构化参数。
    当前仅从文本中粗略识别变调关键词。
    """
    result: dict = {}
    lowered = text.lower()
    if "男转女" in text or "升八度" in text:
        result["pitch"] = 12
    elif "女转男" in text or "降八度" in text:
        result["pitch"] = -12
    return result
