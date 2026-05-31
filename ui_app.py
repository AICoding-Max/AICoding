import os, time, threading, tkinter as tk
from tkinter import ttk
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from src.utils import load_config
from src.script_generator import ScriptGenerator
from src.image_processor import ImageProcessor
from src.tts_generator import TtsGenerator
from src.subtitle_generator import SubtitleGenerator
from src.video_composer import VideoComposer

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Video Generator")
        self.root.geometry("960x700")
        self.root.configure(bg="#1a1a1a")
        self.cfg = load_config()
        self.sg = ScriptGenerator()
        self.ip = ImageProcessor()
        self.tg = TtsGenerator()
        self.sub = SubtitleGenerator()
        self.vc = VideoComposer()
        self.busy = False
        self.last = None
        self._ui()

    def _ui(self):
        tf = tk.Frame(self.root, bg="#252525")
        tf.pack(fill="x", pady=10)
        tk.Label(tf, text="AI Video Generator",
                 font=("Arial", 18, "bold"),
                 fg="#e5e5e5", bg="#252525").pack(side="left", padx=15)

        mf = tk.Frame(self.root, bg="#1e1e1e", padx=10)
        mf.pack(fill="x", padx=5)
        tk.Label(mf, text="Mode:",
                 font=("Arial", 12, "bold"),
                 fg="#e5e5e5").pack(anchor="w", pady=5)

        self.mv = tk.StringVar(value="classic")
        for t, v in [("Classic", "classic"), ("Dance", "dance")]:
            tk.Radiobutton(mf, text=t, value=v,
                var=self.mv, fg="#e5e5e5",
                bg="#1e1e1e", selectcolor="#4caf50",
                font=("Arial", 11),
                command=self._mode).pack(side="left", padx=20)
        inf = tk.Frame(self.root, bg="#1e1e1e", padx=10)
        inf.pack(fill="x", padx=5)
        self.cf = tk.Frame(inf, bg="#1e1e1e")
        self.cf.pack(fill="x", padx=5)
        tk.Label(self.cf, text="Script:", font=("Arial", 11, "bold"), fg="#4caf50").pack(anchor="w", pady=3)
        self.te = tk.Text(self.cf, height=5, wrap="word", font=("Arial", 11), fg="#e5e5e5", bg="#2a2a2a")
        self.te.pack(fill="x", pady=5)
        self.te.insert("end", "Enter script here...")

        self.df = tk.Frame(inf, bg="#1e1e1e")
        tk.Label(self.df, text="Dance:", font=("Arial", 11, "bold"), fg="#4caf50").pack(anchor="w", pady=3)
        self.dsv = tk.StringVar(value="hip hop")
        self.cv = tk.StringVar(value="young woman")
        self.scv = tk.StringVar(value="dance studio")
        for lb, vr in [("Style", self.dsv), ("Character", self.cv), ("Scene", self.scv)]:
            row = tk.Frame(self.df, bg="#1e1e1e")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lb+": ", font=("Arial", 10), fg="#c0c0c0").pack(side="left")
            tk.Entry(row, textvariable=vr, width=30, font=("Arial", 10), bg="#2a2a2a", fg="#e5e5e5").pack(side="left", padx=5)

        af = tk.Frame(self.root, bg="#252525", pady=10)
        af.pack(fill="x", padx=5)
        self.gb = tk.Button(af, text="Generate", font=("Arial", 14, "bold"), bg="#4caf50", fg="white", width=15, command=self._gen)
        self.gb.pack(side="left", padx=20)
        tk.Button(af, text="Open Folder", font=("Arial", 12), bg="#2a2a2a", fg="#c0c0c0", width=10, command=self._open).pack(side="left", padx=20)

        pf = tk.Frame(self.root, bg="#1e1e1e")
        pf.pack(fill="x", padx=5)
        self.pv = tk.IntVar(value=0)
        ttk.Progressbar(pf, variable=self.pv, maximum=100, length=450).pack(padx=20, pady=5)
        self.sv = tk.StringVar(value="Ready")
        tk.Label(pf, textvariable=self.sv, font=("Arial", 11), fg="#c0c0c0", bg="#1e1e1e").pack(pady=5)

        hf = tk.Frame(self.root, bg="#1e1e1e")
        hf.pack(fill="x", padx=5)
        tk.Label(hf, text="History:", font=("Arial", 11, "bold"), fg="#4caf50").pack(anchor="w", pady=3)
        self.hl = tk.Listbox(hf, height=6, font=("Arial", 10), bg="#2a2a2a", fg="#c0c0c0")
        self.hl.pack(fill="x", padx=10)
        self._hist()
        self._mode()

    def _mode(self):
        if self.mv.get() == "classic":
            self.cf.pack(fill="x", padx=5)
            self.df.pack_forget()
        else:
            self.df.pack(fill="x", padx=5)
            self.cf.pack_forget()

    def _gen(self):
        if self.busy: return
        self.busy = True
        self.gb.config(state="disabled")
        self.sv.set("Generating...")
        self.pv.set(0)
        threading.Thread(target=self._run, daemon=True).start()
        self._poll()

    def _run(self):
        try:
            m = self.mv.get()
            if m == "classic":
                tx = self.te.get("1.0", tk.END).strip()
                if not tx:
                    self.sv.set("Enter script")
                    self.busy = False
                    return
                self._sp(15, "Script...")
                seg = self.sg.execute(tx, self.cfg)
                self._sp(30, "Images...")
                imgs = os.path.join(BASE, "assets", "images")
                ip = self.ip.execute(imgs, self.cfg)
                self._sp(50, "Voice...")
                au = None
                if self.cfg.get("audio", {}).get("tts_enabled", True):
                    au = self.tg.execute(seg, self.cfg, None)
                self._sp(70, "Subtitles...")
                self.sub.execute(seg, self.cfg, None)
                self._sp(85, "Video...")
                out = os.path.join(BASE, "output", "videos", "v_%d.mp4" % int(time.time()))
                res = self.vc.execute(ip, au, seg, self.cfg, out)
            else:
                self._sp(15, "Images...")
                imgs = os.path.join(BASE, "assets", "images")
                ip = self.ip.execute(imgs, self.cfg)
                self._sp(35, "Script...")
                txt = "%s dance: %s" % (self.dsv.get(), self.cv.get())
                seg = self.sg.execute(txt, self.cfg)
                self._sp(50, "Voice...")
                au = None
                if self.cfg.get("audio", {}).get("tts_enabled", True):
                    au = self.tg.execute(seg, self.cfg, None)
                self._sp(70, "Subtitles...")
                self.sub.execute(seg, self.cfg, None)
                self._sp(85, "Video...")
                out = os.path.join(BASE, "output", "videos", "v_%d.mp4" % int(time.time()))
                res = self.vc.execute(ip, au, seg, self.cfg, out)
            self.last = res
            self._sp(100, "Done!")
            self.root.after(0, self._hist)
        except Exception as e:
            self.sv.set("Error: %s" % str(e))
        finally:
            self.busy = False
            self.root.after(0, lambda: self.gb.config(state="normal"))

    def _sp(self, p, m):
        self.pv.set(p)
        self.sv.set(m)

    def _poll(self):
        if self.busy: self.root.after(500, self._poll)

    def _open(self):
        d = os.path.join(BASE, "output", "videos")
        if self.last and os.path.exists(self.last): os.startfile(self.last)
        else: os.startfile(d)

    def _hist(self):
        self.hl.delete(0, tk.END)
        d = os.path.join(BASE, "output", "videos")
        if os.path.exists(d):
            for x in sorted(os.listdir(d), reverse=True)[:10]:
                if x.endswith(".mp4"): self.hl.insert(tk.END, x)

if __name__ == "__main__":
    App().root.mainloop()