"""命令行入口：python -m agent.cli --input song.mp3 --model my_singer"""
from __future__ import annotations

import argparse
from pathlib import Path

from agent.orchestrator import CoverRequest, run_cover
from core import config, converter


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 翻唱智能体 命令行工具")
    parser.add_argument("--input", "-i", required=True, help="输入歌曲音频路径")
    parser.add_argument("--model", "-m", required=True, help="音色模型名（models/rvc 下目录名）")
    parser.add_argument("--pitch", "-p", type=int, default=config.DEFAULT_PITCH, help="变调半音数")
    parser.add_argument("--index-rate", type=float, default=config.DEFAULT_INDEX_RATE, help="检索特征比例 0~1")
    parser.add_argument("--f0-method", default=config.DEFAULT_F0_METHOD, help="音高提取算法 rmvpe/crepe/pm")
    parser.add_argument("--output", "-o", default=None, help="输出文件名")
    parser.add_argument("--list-models", action="store_true", help="列出可用音色模型后退出")
    args = parser.parse_args()

    if args.list_models:
        models = converter.list_models()
        print("可用音色模型：", ", ".join(models) if models else "(无，请先下载到 models/rvc/)")
        return

    request = CoverRequest(
        input_audio=Path(args.input),
        model_name=args.model,
        pitch=args.pitch,
        index_rate=args.index_rate,
        f0_method=args.f0_method,
        output_name=args.output,
    )

    def _progress(msg: str, ratio: float) -> None:
        print(f"[{int(ratio * 100):3d}%] {msg}")

    result = run_cover(request, progress=_progress)
    print(f"\n成品已生成: {result.output_path}")


if __name__ == "__main__":
    main()
