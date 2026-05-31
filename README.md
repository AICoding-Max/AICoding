<div align="center">

# 🎬 AICoding

### AI智能视频生成器 | 文案→视频 一键生成

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Stars](https://img.shields.io/github/stars/AICoding-Max/AICoding?style=social)
![Forks](https://img.shields.io/github/forks/AICoding-Max/AICoding?style=social)

**[快速开始](#-快速开始)** · **[在线演示](#-在线演示)** · **[配置指南](#-配置指南)** · **[贡献指南](#-贡献指南)**

</div>

---

## 📖 项目简介

**AICoding** 是一个基于 Python 的开源 AI 视频生成工具，支持通过 Web 界面快速生成短视频。

### 🎯 核心特性

| 特性 | 说明 |
|:---:|------|
| 🎬 | **文生视频** - 输入文案/描述，AI 自动生成视频 |
| 💃 | **舞蹈生成** - 指定舞蹈风格、人物、场景，生成专业舞蹈 |
| 🖼️ | **图生视频** - 上传静态图片，让画面动态化 |
| ⚙️ | **完全自定义** - 支持任何 OpenAI 兼容 API，模型自由选择 |
| 🎨 | **风格预设** - 电影感、动漫风、写实、赛博朋克等多风格 |
| 🌐 | **Web 界面** - 精美深色主题，响应式设计，支持移动端 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- FFmpeg（用于视频处理）
- 一个视频生成 API Key

### 一键安装

```bash
# 1. 克隆仓库
git clone https://github.com/AICoding-Max/AICoding.git
cd AICoding

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

### 🌐 访问

启动后在浏览器打开: **http://localhost:5000**

---

## ⚙️ 配置指南

### 支持的 API 服务

| 服务 | API Base URL | 视频模型 |
|------|--------------|----------|
| **SiliconFlow** | `https://api.siliconflow.cn/v1` | Wan2.1, WAN-X2V |
| **Kling 可灵** | `https://api.klingai.com/v1` | kling-video-v1 |
| **小米 MiMo** | `https://api.xiaomimimo.com/v1` | MiMo-V2.5 |
| **自定义服务** | 任意 OpenAI 兼容 URL | 自动识别 |

### 配置步骤

```
1️⃣ 打开 Web 界面 → 点击「API 配置」展开面板
2️⃣ 点击「+ 添加服务」
3️⃣ 填写 API Name、Base URL、API Key
4️⃣ 点击「获取模型」刷新模型列表
5️⃣ 选择视频模型（必需）
6️⃣ 点击「保存配置」
```

### 模型类型

| 类型 | 必需 | 用途 |
|------|:----:|------|
| 🎬 视频生成模型 | ✅ | 生成视频内容 |
| 🤖 LLM 模型 | 可选 | 生成/优化提示词 |
| 🔊 TTS 语音 | 可选 | 自动配音合成 |

---

## 📖 使用指南

### 模式一：文生视频

```
输入文案 → 选择参数 → 生成视频
```

1. 选择「文生视频」模式
2. 输入视频描述（如：一只小猫在阳光下玩耍）
3. 设置时长（5/10/15/30秒）
4. 选择画面比例（9:16竖屏/16:9横屏/1:1方形）
5. 选择风格预设
6. 点击「🚀 开始生成」

### 模式二：舞蹈生成

```
设定人物 + 舞蹈风格 + 场景 → 生成舞蹈视频
```

1. 选择「舞蹈生成」模式
2. 选择舞蹈风格（Hip Hop/K-Pop/芭蕾/街舞等）
3. 描述人物（如：穿红裙的女孩）
4. 描述场景（如：舞台、城市街道）
5. 点击「🚀 开始生成」

### 模式三：图生视频

```
上传图片 → 添加动态效果 → 生成视频
```

1. 选择「图生视频」模式
2. 输入图片 URL
3. 描述运动效果（如：缓慢移动、摇摆）
4. 点击「🚀 开始生成」

---

## 📁 项目结构

```
AICoding/
├── 📄 app.py                 # Flask 后端服务（主入口）
├── 📄 main.py                # CLI 命令行入口
├── 📄 ui_app.py              # 桌面 GUI 应用
├── 📄 requirements.txt       # Python 依赖清单
├── 📄 README.md              # 项目文档
│
├── 📁 config/                # 配置文件目录
│   └── user_settings.json    # 用户配置（自动生成）
│
├── 📁 templates/             # Web 模板
│   └── index.html            # 主界面（单文件应用）
│
├── 📁 src/                   # 核心模块
│   ├── video_composer.py     # 视频合成
│   ├── image_processor.py    # 图片处理
│   ├── tts_generator.py      # 语音合成
│   ├── subtitle_generator.py # 字幕生成
│   └── utils.py              # 工具函数
│
├── 📁 assets/                # 素材资源
│   ├── images/               # 示例图片
│   └── music/                # 背景音乐
│
└── 📁 output/                # 输出目录
    └── videos/               # 生成的视频
```

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端** | Python 3.10+, Flask |
| **前端** | HTML5, CSS3, JavaScript (Vanilla) |
| **视频处理** | MoviePy, OpenCV, FFmpeg |
| **图片处理** | Pillow |
| **语音合成** | Edge-TTS |
| **AI 集成** | OpenAI 兼容 API 格式 |

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

```bash
# 1. Fork 本仓库

# 2. 创建特性分支
git checkout -b feature/AmazingFeature

# 3. 提交更改
git commit -m 'feat: 添加新功能'

# 4. 推送到分支
git push origin feature/AmazingFeature

# 5. 打开 Pull Request
```

### 提交规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [MoviePy](https://zulko.github.io/moviepy/) - 视频处理
- [Edge-TTS](https://rany2.github.io/edge-tts/) - 语音合成
- [OpenAI](https://openai.com/) - API 兼容格式

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by [AICoding-Max](https://github.com/AICoding-Max)

</div>
