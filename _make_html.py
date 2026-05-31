#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Video Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a1a;--bg2:#12122a;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.08);--accent:#6366f1;--accent2:#8b5cf6;--cyan:#22d3ee;--text:#fff;--text2:rgba(255,255,255,0.6);--text3:rgba(255,255,255,0.4);--success:#10b981;--error:#ef4444;--gradient:linear-gradient(135deg,#6366f1,#8b5cf6,#a855f7);--glass:rgba(255,255,255,0.05);--shadow:0 8px 32px rgba(0,0,0,0.4);--r:20px;--r2:12px}
html{scroll-behavior:smooth}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 20% 80%,rgba(99,102,241,0.15) 0%,transparent 50%),radial-gradient(circle at 80% 20%,rgba(139,92,246,0.15) 0%,transparent 50%);pointer-events:none}
.c{max-width:1200px;margin:0 auto;padding:20px;position:relative;z-index:1}
header{text-align:center;padding:50px 20px 30px}
header h1{font-size:2.5rem;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
header p{color:var(--text2);font-size:1.1rem}
.stats{display:flex;justify-content:center;gap:40px;margin:30px 0;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:var(--r);backdrop-filter:blur(10px)}
.stat{text-align:center}.stat-val{font-size:1.8rem;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.stat-lbl{color:var(--text3);font-size:.8rem;margin-top:4px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;margin-bottom:24px;backdrop-filter:blur(10px)}
.card-head{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;background:var(--glass);cursor:pointer;border-bottom:1px solid var(--border)}
.card-head h2{display:flex;align-items:center;gap:10px;font-size:1.1rem}
.card-head .icon{width:36px;height:36px;background:var(--gradient);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.card-head .toggle{color:var(--text3);font-size:.85rem}
.card-body{display:none;padding:24px}.card-body.show{display:block}
.svc{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:20px;margin-bottom:16px}
.svc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.svc-name{font-weight:600;display:flex;align-items:center;gap:8px}.dot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 8px var(--success)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.fg{display:flex;flex-direction:column;gap:6px}.fg.full{grid-column:1/-1}
.fg label{font-size:.8rem;color:var(--text2);font-weight:500}
.fg input,.fg select{padding:12px 14px;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:.9rem}
.fg input:focus,.fg select:focus{outline:none;border-color:var(--accent)}
.fg .hint{font-size:.7rem;color:var(--text3);margin-top:2px}
.btn-row{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
.btn{padding:10px 20px;border:none;border-radius:8px;font-weight:600;font-size:.85rem;cursor:pointer;transition:all .3s}
.btn-p{background:var(--gradient);color:#fff}.btn-p:hover{transform:translateY(-2px);box-shadow:0 4px 20px rgba(99,102,241,0.4)}
.btn-s{background:rgba(255,255,255,0.08);color:var(--text);border:1px solid var(--border)}.btn-s:hover{border-color:var(--accent)}
.btn-d{background:rgba(239,68,68,0.15);color:var(--error);border:1px solid rgba(239,68,68,0.3)}
.modes{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.mode{padding:24px;background:var(--card);border:2px solid var(--border);border-radius:var(--r);cursor:pointer;transition:all .3s;text-align:center}
.mode:hover{border-color:var(--accent)}.mode.active{border-color:var(--accent);background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));box-shadow:0 0 30px rgba(99,102,241,0.2)}
.mode-icon{font-size:2.5rem;margin-bottom:12px}.mode-title{font-size:1rem;font-weight:600;margin-bottom:6px}.mode-desc{color:var(--text3);font-size:.8rem}
.opts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}
.opt{background:var(--card);border:1px solid var(--border);border-radius:var(--r2);padding:14px}
.opt label{display:block;font-size:.75rem;color:var(--text3);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px}
.opt select{width:100%;padding:8px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;color:var(--text)}
.input-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:24px;margin-bottom:20px}
.input-card h3{font-size:1rem;font-weight:600;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.inp-group{margin-bottom:16px}.inp-group label{display:block;margin-bottom:6px;color:var(--text2);font-size:.9rem}
.inp-group textarea,.inp-group input{width:100%;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.95rem;resize:vertical}
.inp-group textarea{min-height:100px}
.inp-group textarea:focus,.inp-group input:focus{outline:none;border-color:var(--accent)}
.gen-sec{text-align:center;margin:28px 0}
.gen-btn{padding:18px 50px;background:var(--gradient);border:none;border-radius:14px;color:#fff;font-size:1.1rem;font-weight:700;cursor:pointer;box-shadow:0 8px 30px rgba(99,102,241,0.4);transition:all .3s;display:inline-flex;align-items:center;gap:10px}
.gen-btn:hover{transform:translateY(-2px) scale(1.02)}.gen-btn:disabled{opacity:.6;cursor:not-allowed;transform:none}
.prog{display:none;margin:24px 0}.prog.show{display:block}
.prog-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px;text-align:center}
.prog-pct{font-size:2rem;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
.prog-bar{height:10px;background:var(--bg2);border-radius:5px;overflow:hidden;margin:16px 0}
.prog-fill{height:100%;background:var(--gradient);width:0%;transition:width .5s}
.prog-text{color:var(--text2)}
.result{display:none;margin:24px 0}.result.show{display:block}
.result-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px;text-align:center}
.result-card video{width:100%;max-width:600px;border-radius:var(--r);border:2px solid var(--accent);margin:14px 0}
.dl-btn{display:inline-flex;align-items:center;gap:8px;padding:14px 36px;background:var(--success);border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer;text-decoration:none}
.history{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px}
.history h2{font-size:1.1rem;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.h-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.h-item{display:flex;justify-content:space-between;align-items:center;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);cursor:pointer;transition:all .3s}
.h-item:hover{border-color:var(--accent);transform:translateY(-2px)}
.h-name{font-weight:500;display:flex;align-items:center;gap:6px}.h-name::before{content:'';width:6px;height:6px;background:var(--accent);border-radius:50%}
.h-size{color:var(--text3);font-size:.8rem}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(100px);padding:14px 28px;background:var(--bg2);border:1px solid var(--border);border-radius:10px;font-weight:500;opacity:0;transition:all .4s;z-index:1000}
.toast.show{transform:translateX(-50%) translateY(0);opacity:1}
.toast.success{border-color:var(--success)}.toast.error{border-color:var(--error)}
@media(max-width:768px){.modes,.opts,.form-row{grid-template-columns:1fr}header h1{font-size:1.8rem}}
</style>
</head>
<body>
<div class="c">
  <header>
    <h1>AI Video Studio</h1>
    <p>自定义API · 任意模型 · 一键生成专业AI视频</p>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-val">∞</div><div class="stat-lbl">API 服务</div></div>
    <div class="stat"><div class="stat-val">3</div><div class="stat-lbl">生成模式</div></div>
    <div class="stat"><div class="stat-val">6+</div><div class="stat-lbl">风格预设</div></div>
    <div class="stat"><div class="stat-val">100%</div><div class="stat-lbl">完全自定义</div></div>
  </div>

  <!-- API Config -->
  <div class="card">
    <div class="card-head" onclick="toggleConfig()">
      <h2><div class="icon">⚙️</div> API 配置中心</h2>
      <div class="toggle" id="config-toggle">展开 ▼</div>
    </div>
    <div class="card-body" id="config-body">
      <div id="services-list"></div>
      <div class="btn-row">
        <button class="btn btn-s" onclick="addService()">➕ 添加API服务</button>
        <button class="btn btn-p" onclick="saveConfig()">💾 保存配置</button>
      </div>
      <div class="fg" style="margin-top:16px">
        <label>🔊 TTS 语音（用于配音）</label>
        <select id="tts-voice" style="max-width:280px">
          <option value="zh-CN-XiaoxiaoNeural">晓晓 (女声)</option>
          <option value="zh-CN-YunxiNeural">云希 (男声)</option>
          <option value="zh-CN-XiaoyiNeural">晓伊 (女声2)</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Mode Selection -->
  <div class="modes">
    <div class="mode active" onclick="switchMode('classic',this)">
      <div class="mode-icon">✨</div>
      <div class="mode-title">文生视频</div>
      <div class="mode-desc">文案 → AI生成视频</div>
    </div>
    <div class="mode" onclick="switchMode('dance',this)">
      <div class="mode-icon">💃</div>
      <div class="mode-title">舞蹈生成</div>
      <div class="mode-desc">风格+人物 → 舞蹈视频</div>
    </div>
    <div class="mode" onclick="switchMode('i2v',this)">
      <div class="mode-icon">🖼️</div>
      <div class="mode-title">图生视频</div>
      <div class="mode-desc">静态图片 → 动态视频</div>
    </div>
  </div>

  <!-- Options -->
  <div class="opts">
    <div class="opt">
      <label>⏱️ 视频时长</label>
      <select id="duration"><option value="5">5秒</option><option value="10" selected>10秒</option><option value="15">15秒</option><option value="20">20秒</option></select>
    </div>
    <div class="opt">
      <label>📐 画面比例</label>
      <select id="aspect"><option value="9:16" selected>竖屏 9:16</option><option value="16:9">横屏 16:9</option><option value="1:1">方形 1:1</option></select>
    </div>
    <div class="opt">
      <label>🎨 画面风格</label>
      <select id="style-prefix">
        <option value="">默认</option>
        <option value="cinematic, movie lighting" selected>电影感</option>
        <option value="anime style, studio ghibli">动漫风</option>
        <option value="realistic, photorealistic, 8K">写实</option>
        <option value="cyberpunk, neon lights">赛博朋克</option>
        <option value="watercolor, artistic">水彩艺术</option>
      </select>
    </div>
  </div>

  <!-- Input -->
  <div class="input-card" id="classic-input">
    <h3>📝 视频描述</h3>
    <div class="inp-group">
      <textarea id="text" placeholder="详细描述你想要的视频内容...">一个穿着白色连衣裙的漂亮女孩在樱花树下优雅地跳舞，花瓣飘落，电影质感</textarea>
    </div>
  </div>

  <div class="input-card" id="dance-input" style="display:none">
    <h3>💃 舞蹈设置</h3>
    <div class="inp-group"><label>舞蹈风格</label><input id="dance-style" value="hip hop"></div>
    <div class="inp-group"><label>人物描述</label><input id="char" value="a beautiful young woman in white dress"></div>
    <div class="inp-group"><label>场景描述</label><input id="scene" value="modern dance studio with neon lights"></div>
  </div>

  <div class="input-card" id="i2v-input" style="display:none">
    <h3>🖼️ 图片设置</h3>
    <div class="inp-group"><label>图片 URL</label><input id="img-url" placeholder="https://..."></div>
    <div class="inp-group"><label>运动描述</label><textarea id="motion">the person starts dancing gracefully, camera slowly zooms in</textarea></div>
  </div>

  <!-- Generate -->
  <div class="gen-sec">
    <button class="gen-btn" id="gen-btn" onclick="generate()">
      <span id="spinner" style="display:none;width:18px;height:18px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 1s linear infinite"></span>
      <span id="btn-text">🚀 开始生成</span>
    </button>
  </div>
  <style>@keyframes spin{to{transform:rotate(360deg)}}</style>

  <!-- Progress -->
  <div class="prog" id="prog">
    <div class="prog-card">
      <div class="prog-pct" id="prog-pct">0%</div>
      <div class="prog-bar"><div class="prog-fill" id="prog-fill"></div></div>
      <div class="prog-text" id="prog-text">准备中...</div>
    </div>
  </div>

  <!-- Result -->
  <div class="result" id="result">
    <div class="result-card">
      <h2>🎉 生成完成</h2>
      <video id="vid" controls></video><br>
      <button class="dl-btn" id="dl-btn">⬇️ 下载视频</button>
    </div>
  </div>

  <!-- History -->
  <div class="history">
    <h2>📁 历史记录</h2>
    <div class="h-grid" id="h-list"><p style="color:var(--text3);text-align:center;grid-column:1/-1;padding:30px">暂无记录</p></div>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
let mode='classic',running=false,apiServices=[];
function toggleConfig(){const b=document.getElementById('config-body'),t=document.getElementById('config-toggle');b.classList.toggle('show');t.textContent=b.classList.contains('show')?'收起 ▲':'展开 ▼'}
async function loadConfig(){try{const r=await fetch('/api/config'),d=await r.json();apiServices=d.services||[];renderServices();document.getElementById('tts-voice').value=d.tts_voice||'zh-CN-XiaoxiaoNeural'}catch(e){console.error(e)}}
function renderServices(){const c=document.getElementById('services-list');c.innerHTML='';apiServices.forEach((s,i)=>{const d=document.createElement('div');d.className='svc';d.innerHTML=`<div class="svc-head"><div class="svc-name"><span class="dot"></span>${s.name||'API '+(i+1)}</div><button class="btn btn-d" onclick="removeService(${i})">删除</button></div><div class="form-row"><div class="fg"><label>服务名称</label><input value="${s.name||''}" onchange="updateService(${i},'name',this.value)" placeholder="例如：我的Kling API"></div><div class="fg"><label>API Key</label><input type="password" value="${s.key||''}" onchange="updateService(${i},'key',this.value)" placeholder="sk-xxx"></div><div class="fg full"><label>API URL</label><input value="${s.url||''}" onchange="updateService(${i},'url',this.value)" placeholder="https://api.xxx.com/v1"><div class="hint">兼容 OpenAI /api/models 格式的 API 地址</div></div><div class="fg"><label>🎬 视频模型（必需）</label><select id="vm-${i}"><option value="">刷新获取</option></select></div><div class="fg"><label>🧠 文本/LLM模型（可选）</label><select id="lm-${i}"><option value="">刷新获取</option></select></div></div><div class="btn-row"><button class="btn btn-s" onclick="refreshModels(${i})">🔄 刷新模型</button></div>`;c.appendChild(d);if(s.key&&s.url)setTimeout(()=>refreshModels(i),100)})}
function addService(){apiServices.push({name:'',key:'',url:''});renderServices()}
function removeService(i){apiServices.splice(i,1);renderServices()}
function updateService(i,f,v){apiServices[i][f]=v}
async function refreshModels(i){const s=apiServices[i];if(!s.key||!s.url){showToast('请先填写Key和URL','error');return}try{const r=await fetch('/api/models?api_key='+encodeURIComponent(s.key)+'&api_url='+encodeURIComponent(s.url)),d=await r.json();const vs=document.getElementById('vm-'+i),ls=document.getElementById('lm-'+i);vs.innerHTML='';ls.innerHTML='';(d.video||[]).forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.name||m.id;vs.appendChild(o)});(d.llm||[]).forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.name||m.id;ls.appendChild(o)});if(!d.video?.length)vs.innerHTML='<option value=\"\">无视频模型</option>';if(!d.llm?.length)ls.innerHTML='<option value=\"\">无LLM模型</option>';showToast('模型已刷新','success')}catch(e){showToast('获取模型失败','error')}}
async function saveConfig(){apiServices.forEach((s,i)=>{s.video_model=document.getElementById('vm-'+i)?.value||'';s.llm_model=document.getElementById('lm-'+i)?.value||''});try{const r=await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({services:apiServices,tts_voice:document.getElementById('tts-voice').value})});showToast(r.ok?'已保存':'保存失败',r.ok?'success':'error')}catch(e){showToast('保存失败','error')}}
function switchMode(m,el){mode=m;document.querySelectorAll('.mode').forEach(c=>c.classList.remove('active'));el.classList.add('active');document.getElementById('classic-input').style.display=m==='classic'?'block':'none';document.getElementById('dance-input').style.display=m==='dance'?'block':'none';document.getElementById('i2v-input').style.display=m==='i2v'?'block':'none'}
function showToast(m,t){const e=document.getElementById('toast');e.textContent=m;e.className='toast show '+t;setTimeout(()=>e.classList.remove('show'),3000)}
async function generate(){if(running)return;running=true;const b=document.getElementById('gen-btn');document.getElementById('spinner').style.display='inline-block';document.getElementById('btn-text').textContent='生成中...';b.disabled=true;document.getElementById('prog').classList.add('show');document.getElementById('result').classList.remove('show');let body={mode,duration:document.getElementById('duration').value,aspect:document.getElementById('aspect').value,style_prefix:document.getElementById('style-prefix').value};if(mode==='classic')body.text=document.getElementById('text').value;else if(mode==='dance'){body.style=document.getElementById('dance-style').value;body.char=document.getElementById('char').value;body.scene=document.getElementById('scene').value}else if(mode==='i2v'){body.image=document.getElementById('img-url').value;body.motion=document.getElementById('motion').value}try{const r=await fetch('/api/gen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){const e=await r.json();throw new Error(e.err||'生成失败')}poll()}catch(e){showToast(e.message,'error');resetUI()}}
async function poll(){try{const r=await fetch('/api/progress'),d=await r.json();document.getElementById('prog-fill').style.width=d.pct+'%';document.getElementById('prog-pct').textContent=d.pct+'%';document.getElementById('prog-text').textContent=d.msg;if(d.status==='done'){const vp='/video/'+d.path.split(/[\\\\/]/).pop();document.getElementById('vid').src=vp;document.getElementById('dl-btn').onclick=()=>{const a=document.createElement('a');a.href=vp;a.download='video.mp4';a.click()};document.getElementById('result').classList.add('show');loadHistory();resetUI();showToast('生成完成！','success')}else if(d.status==='err'){showToast('错误：'+d.msg,'error');resetUI()}else{setTimeout(poll,1000)}}catch(e){showToast('获取进度失败','error');resetUI()}}
function resetUI(){running=false;document.getElementById('spinner').style.display='none';document.getElementById('btn-text').textContent='🚀 开始生成';document.getElementById('gen-btn').disabled=false;setTimeout(()=>document.getElementById('prog').classList.remove('show'),2000)}
async function loadHistory(){try{const r=await fetch('/api/videos'),d=await r.json();const l=document.getElementById('h-list');if(!d.length){l.innerHTML='<p style=\"color:var(--text3);text-align:center;grid-column:1/-1;padding:30px\">暂无记录</p>';return}l.innerHTML=d.map(v=>`<div class="h-item" onclick="playVideo('${v.name}')"><span class="h-name">${v.name.replace('.mp4','')}</span><span class="h-size">${(v.size/1024/1024).toFixed(2)} MB</span></div>`).join('')}catch(e){console.error(e)}}
function playVideo(n){const vp='/video/'+n;document.getElementById('vid').src=vp;document.getElementById('dl-btn').onclick=()=>{const a=document.createElement('a');a.href=vp;a.download=n;a.click()};document.getElementById('result').classList.add('show');document.getElementById('result').scrollIntoView({behavior:'smooth'})}
document.addEventListener('DOMContentLoaded',()=>{loadConfig();loadHistory()});
</script>
</body>
</html>'''

os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done')
