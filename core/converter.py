"""歌声音色转换模块（方案A：调用外部 RVC-WebUI 整合包）。

本模块不直接依赖 rvc-python（其依赖已停止维护的 fairseq，Windows 无法安装），
而是通过命令行调用你单独部署的官方 RVC-WebUI 整合包中的 tools/infer_cli.py。

准备工作：
1. 下载官方 RVC-WebUI 整合包并解压，例如到 D:\\AI\\RVC-WebUI
2. 在 core/config.py 设置 RVC_WEBUI_DIR，或设置环境变量 RVC_WEBUI_DIR
3. 从 HuggingFace 下载 RVC 音色模型（.pth，可选 .index），放入本项目 models/rvc/<音色名>/
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from core import config


class ConversionError(RuntimeError):
    pass


def list_models() -> list[str]:
    """列出 models/rvc 下可用的音色模型名称（含 .pth 的子目录名）。"""
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


def _check_rvc_webui() -> None:
    if not config.RVC_WEBUI_DIR.exists():
        raise ConversionError(
            f"未找到 RVC-WebUI 目录: {config.RVC_WEBUI_DIR}\n"
            "请下载官方整合包并在 core/config.py 设置 RVC_WEBUI_DIR，"
            "或设置环境变量 RVC_WEBUI_DIR。"
        )
    if not config.RVC_INFER_CLI.exists():
        raise ConversionError(f"未找到 RVC 推理脚本: {config.RVC_INFER_CLI}")
    if not config.RVC_PYTHON.exists():
        raise ConversionError(
            f"未找到 RVC-WebUI 自带 Python: {config.RVC_PYTHON}\n"
            "请检查整合包 runtime 目录，或设置环境变量 RVC_PYTHON。"
        )


def convert(
    vocals_path: str | Path,
    model_name: str,
    output_path: str | Path,
    pitch: int = config.DEFAULT_PITCH,
    index_rate: float = config.DEFAULT_INDEX_RATE,
    f0_method: str = config.DEFAULT_F0_METHOD,
) -> Path:
    """将人声音频转换为目标音色，通过调用 RVC-WebUI 的 infer_cli。

    参数：
        vocals_path: 干声（分离后的人声）路径
        model_name: 本项目 models/rvc 下的模型目录名
        output_path: 转换后人声输出路径
        pitch: 变调半音数（男声转女声常用 +12）
        index_rate: 检索特征混合比例 0~1
        f0_method: 音高提取算法 rmvpe / crepe / pm / harvest
    """
    _check_rvc_webui()

    vocals_path = Path(vocals_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pth, index = _resolve_model(model_name)

    cmd = [
        str(config.RVC_PYTHON), str(config.RVC_INFER_CLI),
        "--f0up_key", str(pitch),
        "--input_path", str(vocals_path),
        "--opt_path", str(output_path),
        "--model_name", str(pth),
        "--index_path", str(index) if index else "",
        "--index_rate", str(index_rate),
        "--f0method", f0_method,
        "--device", config.DEVICE,
    ]

    proc = subprocess.run(
        cmd, cwd=str(config.RVC_WEBUI_DIR), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise ConversionError(
            f"RVC 转换失败 (exit {proc.returncode}):\n{proc.stderr or proc.stdout}"
        )

    if not output_path.exists():
        raise ConversionError(
            f"RVC 转换未生成输出文件: {output_path}\n输出日志:\n{proc.stdout}"
        )
    return output_path
