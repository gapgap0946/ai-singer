"""歌声音色转换模块，基于 RVC (rvc-python)。"""
from __future__ import annotations

from pathlib import Path

from core import config


class ConversionError(RuntimeError):
    pass


def list_models() -> list[str]:
    """列出 models/rvc 下可用的音色模型名称（子目录名）。"""
    if not config.RVC_MODELS_DIR.exists():
        return []
    names = []
    for d in config.RVC_MODELS_DIR.iterdir():
        if d.is_dir() and any(d.glob("*.pth")):
            names.append(d.name)
    return sorted(names)


def _resolve_model(model_name: str) -> tuple[Path, Path | None]:
    model_dir = config.RVC_MODELS_DIR / model_name
    if not model_dir.exists():
        raise ConversionError(f"未找到音色模型目录: {model_dir}")
    pth = next(iter(model_dir.glob("*.pth")), None)
    if pth is None:
        raise ConversionError(f"模型目录缺少 .pth 权重文件: {model_dir}")
    index = next(iter(model_dir.glob("*.index")), None)
    return pth, index


def convert(
    vocals_path: str | Path,
    model_name: str,
    output_path: str | Path,
    pitch: int = config.DEFAULT_PITCH,
    index_rate: float = config.DEFAULT_INDEX_RATE,
    f0_method: str = config.DEFAULT_F0_METHOD,
) -> Path:
    """将人声音频转换为目标音色。

    参数：
        vocals_path: 干声（分离后的人声）路径
        model_name: models/rvc 下的模型目录名
        output_path: 转换后人声输出路径
        pitch: 变调半音数（男声转女声常用 +12）
        index_rate: 检索特征混合比例 0~1
        f0_method: 音高提取算法，如 rmvpe / crepe / pm
    """
    try:
        from rvc_python.infer import RVCInference
    except ImportError as e:
        raise ConversionError(
            "未安装 rvc-python，请先执行 pip install rvc-python"
        ) from e

    vocals_path = Path(vocals_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pth, index = _resolve_model(model_name)

    rvc = RVCInference(device=config.DEVICE)
    rvc.load_model(str(pth), index_path=str(index) if index else "")
    rvc.set_params(f0up_key=pitch, f0method=f0_method, index_rate=index_rate)
    rvc.infer_file(str(vocals_path), str(output_path))

    if not output_path.exists():
        raise ConversionError(f"转换未生成输出文件: {output_path}")
    return output_path
