#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Video Generator</title>
<style>
:root {
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
  --bg-card: #16213e;
  --accent: #00d4ff;
  --accent-hover: #00b8d9;
  --accent-glow: rgba(0, 212, 255, 0.3);
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --success: #00e676;
  --warning: #ffab00;
  --danger: #ff5252;
  --border: rgba(255,255,255,0.1);
  --radius: 16px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: hidden;
}
.container { max-width: 1200px; margin: 0 auto; padding: 40px 24px; }
header { text-align: center; margin-bottom: 48px; }
header h1 {
  font-size: 2.5rem;
  background: linear-gradient(135deg, var(--accent), #7c4dff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}
header p { color: var(--text-secondary); font-size: 1.1rem; }
.mode-toggle { display: flex; gap: 16px; justify-content: center; margin-bottom: 40px; }
.mode-btn {
  padding: 16px 32px;
  border: 2px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}
.mode-btn:hover { border-color: var(--accent); background: rgba(0, 212, 255, 0.1); }
.mode-btn.active {
  border-color: var(--accent);
  background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(124,77,255,0.2));
  box-shadow: 0 0 30px var(--accent-glow);
}
.mode-desc { font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px; font-weight: 400; }
.main-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 32px;
  border: 1px solid var(--border);
  margin-bottom: 32px;
}
.form-group { margin-bottom: 24px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--accent); }
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 14px 18px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: border-color 0.3s;
}
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 20px var(--accent-glow);
}
.form-group textarea { min-height: 120px; resize: vertical; }
.gen-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, var(--accent), #7c4dff);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}
.gen-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 40px var(--accent-glow); }
.gen-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.progress-section { display: none; margin-top: 24px; }
.progress-section.show { display: block; }
.progress-bar { height: 8px; background: var(--bg-primary); border-radius: 4px; overflow: hidden; margin-bottom: 12px; }
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #7c4dff);
  border-radius: 4px;
  transition: width 0.5s ease;
  width: 0%;
}
.progress-text { color: var(--text-secondary); text-align: center; }
.result-section { display: none; margin-top: 24px; text-align: center; }
.result-section.show { display: block; }
video { width: 100%; max-width: 500px; border-radius: var(--radius); border: 2px solid var(--accent); margin: 16px 0; }
.download-btn {
  display: inline-block;
  padding: 14px 32px;
  background: var(--success);
  border: none;
  border-radius: 12px;
  color: #000;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
}
.download-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,230,118,0.4); }
.history-section {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 32px;
  border: 1px solid var(--border);
}
.history-section h2 { margin-bottom: 20px; color: var(--accent); }
.history-list { display: grid; gap: 12px; }
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.3s;
}
.history-item:hover { border-color: var(--accent); transform: translateX(8px); }
.history-name { font-weight: 600; }
.history-size { color: var(--text-secondary); font-size: 0.9rem; }
.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 16px 24px;
  background: var(--danger);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  transform: translateY(100px);
  opacity: 0;
  transition: all 0.4s;
}
.toast.show { transform: translateY(0); opacity: 1; }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>AI Video Generator</h1>
    <p>输入文案，自动生成短视频 | 支持经典模式 & 舞蹈模式</p>
  </header>
  <div class="mode-toggle">
    <button class="mode-btn active" onclick="switchMode('classic')">
      <div>经典模式</div>
      <div class="mode-desc">文案 → 图片轮播视频</div>
    </button>
    <button class="mode-btn" onclick="switchMode('dance')">
      <div>舞蹈模式</div>
      <div class="mode-desc">音乐 → AI 生成舞蹈</div>
    </button>
  </div>
  <div class="main-card">
    <div id="classic-form">
      <div class="form-group">
        <label>视频文案 / 主题</label>
        <textarea id="classic-text" placeholder="例如：今天分享5个提升效率的AI工具...">今天分享5个提升效率的AI工具</textarea>
      </div>
      <div class="form-group">
        <label>提示词优化 (可选)</label>
        <input type="text" id="classic-prompt" placeholder="用于 AI 图片生成的风格描述">
      </div>
    </div>
    <div id="dance-form" style="display:none;">
      <div class="form-group">
        <label>舞蹈风格</label>
        <input type="text" id="dance-style" placeholder="例如：hip hop, jazz, contemporary" value="hip hop">
      </div>
      <div class="form-group">
        <label>人物描述</label>
        <input type="text" id="dance-character" placeholder="例如：a young woman in white dress" value="a young woman">
      </div>
      <div class="form-group">
        <label>场景描述</label>
        <input type="text" id="dance-scene" placeholder="例如：dance studio, stage" value="dance studio">
      </div>
    </div>
    <button class="gen-btn" id="gen-btn" onclick="generate()">开始生成</button>
    <div class="progress-section" id="progress-section">
      <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
      </div>
      <div class="progress-text" id="progress-text">准备中...</div>
    </div>
    <div class="result-section" id="result-section">
      <video id="result-video" controls></video>
      <br>
      <a class="download-btn" id="download-btn" download>下载视频</a>
    </div>
  </div>
  <div class="history-section">
    <h2>历史记录</h2>
    <div class="history-list" id="history-list">
      <p style="color:var(--text-secondary)">暂无视频记录</p>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
let currentMode = 'classic';
let isGenerating = false;
function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  event.target.closest('.mode-btn').classList.add('active');
  document.getElementById('classic-form').style.display = mode === 'classic' ? 'block' : 'none';
  document.getElementById('dance-form').style.display = mode === 'dance' ? 'block' : 'none';
}
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}
async function generate() {
  if (isGenerating) return;
  isGenerating = true;
  const btn = document.getElementById('gen-btn');
  btn.disabled = true;
  btn.textContent = '生成中...';
  document.getElementById('progress-section').classList.add('show');
  document.getElementById('result-section').classList.remove('show');
  let body = { mode: currentMode };
  if (currentMode === 'classic') {
    body.text = document.getElementById('classic-text').value;
  } else {
    body.dance_style = document.getElementById('dance-style').value;
    body.character = document.getElementById('dance-character').value;
    body.scene = document.getElementById('dance-scene').value;
  }
  try {
    const res = await fetch('/api/gen', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.err || '生成失败');
    }
    pollProgress();
  } catch (e) {
    showToast(e.message);
    resetUI();
  }
}
async function pollProgress() {
  try {
    const res = await fetch('/api/progress');
    const data = await res.json();
    document.getElementById('progress-fill').style.width = data.pct + '%';
    document.getElementById('progress-text').textContent = data.msg;
    if (data.status === 'done') {
      const videoPath = '/video/' + data.path.split(/[\\/]/).pop();
      document.getElementById('result-video').src = videoPath;
      document.getElementById('download-btn').href = videoPath;
      document.getElementById('result-section').classList.add('show');
      loadHistory();
      resetUI();
      showToast('生成完成！');
    } else if (data.status === 'err') {
      showToast('错误：' + data.msg);
      resetUI();
    } else {
      setTimeout(pollProgress, 500);
    }
  } catch (e) {
    showToast('获取进度失败');
    resetUI();
  }
}
function resetUI() {
  isGenerating = false;
  const btn = document.getElementById('gen-btn');
  btn.disabled = false;
  btn.textContent = '开始生成';
  setTimeout(() => {
    document.getElementById('progress-section').classList.remove('show');
  }, 2000);
}
async function loadHistory() {
  try {
    const res = await fetch('/api/videos');
    const data = await res.json();
    const list = document.getElementById('history-list');
    if (data.length === 0) {
      list.innerHTML = '<p style="color:var(--text-secondary)">暂无视频记录</p>';
      return;
    }
    list.innerHTML = data.map(v => 
      <div class="history-item" onclick="playVideo('')">
        <span class="history-name"></span>
        <span class="history-size"> KB</span>
      </div>
    ).join('');
  } catch (e) {
    console.error('Load history failed:', e);
  }
}
function playVideo(name) {
  const videoPath = '/video/' + name;
  document.getElementById('result-video').src = videoPath;
  document.getElementById('download-btn').href = videoPath;
  document.getElementById('result-section').classList.add('show');
  document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
}
loadHistory();
</script>
</body>
</html>'''

os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print('Generated: templates/index.html')
