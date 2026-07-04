"""FastAPI 后端：提供上传、翻唱处理、结果下载与模型列表接口。

启动： python -m api.server
"""
from __future__ import annotations

import shutil
import traceback
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from agent.orchestrator import CoverRequest, run_cover
from core import config, converter

app = FastAPI(title="AI 翻唱智能体", version="0.1.0")

WEB_DIR = config.BASE_DIR / "web"


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AI 翻唱智能体</h1><p>前端页面缺失。</p>")


@app.get("/api/models")
def get_models() -> dict:
    return {"models": converter.list_models()}


@app.post("/api/cover")
async def create_cover(
    file: UploadFile = File(...),
    model: str = Form(...),
    pitch: int = Form(config.DEFAULT_PITCH),
    index_rate: float = Form(config.DEFAULT_INDEX_RATE),
    f0_method: str = Form(config.DEFAULT_F0_METHOD),
) -> dict:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in config.SUPPORTED_AUDIO_EXTS:
        raise HTTPException(400, f"不支持的音频格式: {ext}")

    upload_path = config.UPLOADS_DIR / (file.filename or "input.wav")
    with upload_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    request = CoverRequest(
        input_audio=upload_path,
        model_name=model,
        pitch=pitch,
        index_rate=index_rate,
        f0_method=f0_method,
    )

    try:
        result = run_cover(request)
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(500, f"处理失败: {e}") from e

    return {
        "output": result.output_path.name,
        "steps": result.steps,
        "download_url": f"/api/download/{result.output_path.name}",
    }


@app.get("/api/download/{name}")
def download(name: str) -> FileResponse:
    path = config.OUTPUTS_DIR / name
    if not path.exists():
        raise HTTPException(404, "文件不存在")
    return FileResponse(path, filename=name)


def main() -> None:
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)


if __name__ == "__main__":
    main()
