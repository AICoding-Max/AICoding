# -*- coding: utf-8 -*-
import os

html_path = 'templates/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

guide = '''<div style="background:var(--bg-secondary);border:1px solid var(--card-border);border-radius:12px;padding:20px;margin-bottom:20px"><h4 style="color:var(--accent);margin-bottom:12px">需要的模型类型</h4><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px"><div style="background:var(--bg);padding:16px;border-radius:10px;border:1px solid var(--card-border)"><div style="font-size:1.5rem;margin-bottom:8px">🎬</div><div style="font-weight:600;margin-bottom:4px">视频生成模型</div><div style="font-size:0.8rem;color:var(--text3)">必需。如 Wan2.1、Kling</div></div><div style="background:var(--bg);padding:16px;border-radius:10px;border:1px solid var(--card-border)"><div style="font-size:1.5rem;margin-bottom:8px">🧠</div><div style="font-weight:600;margin-bottom:4px">文本/LLM模型</div><div style="font-size:0.8rem;color:var(--text3)">可选。如 MiMo、GPT</div></div><div style="background:var(--bg);padding:16px;border-radius:10px;border:1px solid var(--card-border)"><div style="font-size:1.5rem;margin-bottom:8px">🔊</div><div style="font-weight:600;margin-bottom:4px">TTS 语音</div><div style="font-size:0.8rem;color:var(--text3)">可选。用于自动配音</div></div></div></div>'''

content = content.replace('<div id="services-list"></div>', guide + '\n      <div id="services-list"></div>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
