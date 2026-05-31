# AI Video Generator

<div align="center">

![AI Video Generator](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Stars](https://img.shields.io/github/stars/AICoding-Max/AICoding?style=social)

**一个完全自定义的AI视频生成工具，支持任何兼容OpenAI格式的API服务**

[快速开始](#-快速开始) · [配置说明](#-配置说明) · [使用指南](#-使用指南)

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **文生视频** | 输入文案描述，AI 自动生成视频 |
| **舞蹈生成** | 指定舞蹈风格、人物、场景，生成专业舞蹈视频 |
| **图生视频** | 上传静态图片，让画面动起来 |
| **自定义API** | 支持任何兼容 OpenAI 格式的 API 服务 |
| **动态模型** | 自动从 API 获取可用模型列表 |
| **风格预设** | 电影感、动漫风、写实、赛博朋克等 6+ 种风格 |
| **Web界面** | 美观的深色主题 Web UI，响应式设计 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 一个视频生成 API Key（如 SiliconFlow、Kling 等）

### 安装

```bash
# 克隆仓库
git clone https://github.com/AICoding-Max/AICoding.git
cd AICoding

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

### 访问

浏览器打开 http://localhost:5000

## ⚙️ 配置说明

### 支持的 API 服务

| 服务 | API URL | 模型示例 |
|------|---------|----------|
| SiliconFlow | `https://api.siliconflow.cn/v1` | Wan2.1, SD3.5, FLUX |
| Kling 可灵 | `https://api.klingai.com/v1` | kling-video-v1 |
| 小米 MiMo | `https://platform.xiaomimimo.com/api/v1` | MiMo-V2.5 |
| 任何兼容 API | 自定义 URL | GPT-4o, Claude 等 |

### 配置步骤

1. 点击「API 配置中心」展开配置面板
2. 点击「+ 添加API服务」
3. 填写服务名称、API Key、API URL
4. 点击「刷新模型」获取可用模型
5. 选择视频模型（必需）
6. 点击「保存配置」

### 模型类型说明

| 图标 | 类型 | 必需 | 说明 |
|------|------|------|------|
| 🎬 | 视频生成模型 | ✅ | 用于生成视频 |
| 🤖 | 文本/LLM模型 | 可选 | 用于生成脚本 |
| 🔊 | TTS 语音 | 可选 | 用于自动配音 |

## 📖 使用指南

### 文生视频

1. 选择「文生视频」模式
2. 输入视频描述
3. 选择时长、比例、风格
4. 点击「开始生成」

### 舞蹈生成

1. 选择「舞蹈生成」模式
2. 填写舞蹈风格（如 hip hop、ballet）
3. 填写人物描述
4. 填写场景描述
5. 点击「开始生成」

### 图生视频

1. 选择「图生视频」模式
2. 输入图片 URL
3. 填写运动描述
4. 点击「开始生成」

## 📁 项目结构

```
AICoding/
├── app.py              # Flask 后端服务
├── main.py             # 命令行入口
├── ui_app.py           # 桌面 GUI
├── requirements.txt    # Python 依赖
├── config/             # 配置文件
│   └── user_settings.json
├── templates/          # Web 界面
│   └── index.html
├── src/                # 核心模块
│   ├── video_composer.py
│   ├── image_processor.py
│   ├── tts_generator.py
│   └── ...
├── assets/             # 素材资源
│   ├── images/
│   └── music/
└── output/             # 输出目录
    └── videos/
```

## 🛠️ 技术栈

- **后端**: Flask, Python
- **前端**: HTML5, CSS3, JavaScript
- **视频处理**: MoviePy, OpenCV
- **图片处理**: Pillow
- **语音合成**: Edge-TTS
- **AI 模型**: 支持任何 OpenAI 兼容 API

## 🤝 贡献

欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 License

本项目基于 MIT License 开源 - 查看 [LICENSE](LICENSE) 了解详情

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [MoviePy](https://zulko.github.io/moviepy/) - 视频处理
- [Edge-TTS](https://rany2.github.io/edge-tts/) - 语音合成
- 所有支持 OpenAI 兼容格式的 API 服务

---

<div align="center>

**[⬆ 回到顶部](#ai-video-generator)**

</div>