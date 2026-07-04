# AI 翻唱智能体 (ai-singer)

一个端到端的 AI 翻唱系统：输入一首歌，自动完成 **人声/伴奏分离 → 歌声音色转换 (RVC) → 混音合成**，并通过 Web 界面与智能体编排层进行交互。

## 功能特性

- 🎤 **人声分离**：基于 [Demucs](https://github.com/facebookresearch/demucs) 将歌曲拆分为人声与伴奏
- 🎨 **歌声转换**：基于 RVC (Retrieval-based Voice Conversion) 将原唱音色替换为目标音色
- 🎚️ **混音合成**：将转换后的人声与原伴奏对齐、混音输出成品
- 🤖 **智能体编排**：用自然语言下达指令，自动规划并执行整条翻唱流水线
- 🌐 **Web 界面**：上传音频、选择音色模型、调节参数、在线试听

## 环境要求

- **操作系统**：Windows / Linux
- **Python**：3.10（推荐）
- **GPU**：NVIDIA 显卡，显存 ≥ 6GB（推理），已安装 CUDA 驱动
- **ffmpeg**：已安装并加入 PATH

## 安装

项目使用独立虚拟环境隔离依赖。

### 1. 创建并激活虚拟环境

```powershell
# Windows PowerShell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3.10 -m venv .venv
source .venv/bin/activate
```

### 2. 安装 PyTorch（CUDA 版本）

先根据你的 CUDA 版本安装 GPU 版 PyTorch（以 CUDA 12.1 为例）：

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. 安装其余依赖

```bash
pip install -r requirements.txt
```

## 模型下载

RVC 音色模型从 [HuggingFace](https://huggingface.co/models?search=rvc) 获取。

1. 找到目标音色模型（通常包含一个 `.pth` 权重文件，可选 `.index` 检索文件）。
2. 将文件放入 `models/rvc/<音色名>/` 目录，例如：

```
models/
└── rvc/
    └── my_singer/
        ├── my_singer.pth
        └── my_singer.index   # 可选，提升音色相似度
```

3. 首次运行时 Demucs 会自动下载分离模型（需联网）。

## 歌声转换方案（重要）

> ⚠️ `rvc-python` 依赖已停止维护的 `fairseq==0.12.2`，在 Windows / Python 3.10 环境**无法安装**。
> 因此本项目采用**解耦方案**：歌声转换环节调用你单独部署的官方 **RVC-WebUI 整合包**，
> 我们的项目负责「人声分离 + 混音 + 编排 + Web 界面」，转换环节通过命令行调用 RVC-WebUI。

### 部署 RVC-WebUI

1. 下载官方整合包：[RVC-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)（推荐带 `runtime` 的 Windows 整合包）。
2. 解压到任意目录，例如 `D:\AI\RVC-WebUI`。
3. 在 [core/config.py](core/config.py) 中设置 `RVC_WEBUI_DIR`，或通过环境变量覆盖：

```powershell
$env:RVC_WEBUI_DIR = "D:\AI\RVC-WebUI"
$env:RVC_PYTHON    = "D:\AI\RVC-WebUI\runtime\python.exe"
```

4. RVC 音色模型（`.pth` / `.index`）仍放在本项目 `models/rvc/<音色名>/` 下即可。

## 运行

```bash
# 启动 Web 服务
python -m api.server
```

打开浏览器访问 http://localhost:8000

## 命令行用法

```bash
python -m agent.cli --input song.mp3 --model my_singer --pitch 0 --output result.wav
```

## 项目结构

```
ai-singer/
├── agent/              # 智能体编排层
│   ├── orchestrator.py # 流水线编排 + 意图解析（预留 LLM 接口）
│   └── cli.py          # 命令行入口
├── core/               # 核心音频处理
│   ├── separator.py    # 人声分离 (Demucs)
│   ├── converter.py    # 歌声转换 (RVC)
│   ├── mixer.py        # 混音后处理
│   └── config.py       # 全局配置
├── api/                # FastAPI 后端
│   └── server.py
├── web/                # 前端页面
│   └── index.html
├── models/             # 音色模型存放目录
├── outputs/            # 处理结果输出目录
└── requirements.txt
```

## 注意事项

- ⚠️ **版权与伦理**：使用他人音色进行翻唱、发布时请遵守声音权、肖像权及歌曲版权相关法律法规，仅供学习研究使用。
- 6GB 显存足够推理；如需训练自己的音色模型，请酌情减小 batch size。

## 许可证

MIT
