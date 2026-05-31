# AI Video Studio

一个完全自定义的AI视频生成工具，支持任何兼容OpenAI格式的视频生成API。

## ? 特性

- ?? **文生视频** - 输入文案，AI自动生成视频
- ?? **舞蹈生成** - 指定舞蹈风格和人物，生成专业舞蹈视频
- ??? **图生视频** - 上传静态图片，让画面动起来
- ?? **完全自定义** - 支持配置任何API服务和模型
- ?? **风格预设** - 电影感、动漫风、写实、赛博朋克等
- ?? **响应式界面** - 美观的深色主题Web界面

## ?? 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

### 访问界面

浏览器打开 http://localhost:5000

## ?? 配置说明

### 支持的API服务

| 服务 | API URL | 说明 |
|------|---------|------|
| SiliconFlow | https://api.siliconflow.cn/v1 | Wan2.1等模型 |
| Kling可灵 | https://api.klingai.com/v1 | 高质量视频生成 |
| 小米MiMo | https://platform.xiaomimimo.com/api/v1 | 文本/LLM模型 |
| 任何兼容API | 自定义 | 兼容OpenAI格式即可 |

### 配置步骤

1. 点击「API 配置中心」展开
2. 点击「添加API服务」
3. 填写服务名称、API Key、API URL
4. 点击「刷新模型」获取可用模型列表
5. 选择「视频模型」（必需）
6. 点击「保存配置」

## ?? 项目结构

```
ai-video-generator/
├── app.py              # Flask后端服务
├── main.py             # 命令行入口
├── ui_app.py           # 桌面GUI
├── requirements.txt    # Python依赖
├── config/             # 配置文件
├── templates/          # Web界面
├── src/                # 核心模块
├── assets/             # 素材资源
└── output/             # 输出目录
```

## ?? 技术栈

- Python 3.10+
- Flask (Web框架)
- MoviePy (视频处理)
- Pillow (图片处理)
- Edge-TTS (语音合成)

## ?? License

MIT License
