import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import edge_tts
import threading
import os
import time

# ==================== 主窗口 ====================
root = tk.Tk()
root.title("Edge TTS - 晓晓语音工具（显示用时）")
root.geometry("780x540")

ttk.Label(root, text="Edge TTS 文本转语音（打碎doro的肉垫）", font=("微软雅黑", 16, "bold")).pack(pady=12)

# 文本输入
ttk.Label(root, text="请输入文本（支持长文本）：", font=("微软雅黑", 10)).pack(anchor="w", padx=20)
text_area = tk.Text(root, height=12, wrap="word", font=("微软雅黑", 10))
text_area.pack(fill="both", expand=True, padx=20, pady=8)

# 控制区
control = ttk.Frame(root)
control.pack(fill="x", padx=20, pady=10)

# 语音选择
voices = {
    "晓晓 - 女声（推荐）": "zh-CN-XiaoxiaoNeural",
    "云溪 - 男声": "zh-CN-YunxiNeural",
    "云扬 - 男声": "zh-CN-YunyangNeural",
    "晓伊 - 女声": "zh-CN-XiaoyiNeural",
    "英文 Aria": "en-US-AriaNeural",
}

ttk.Label(control, text="选择语音：").grid(row=0, column=0, sticky="w", pady=6)
voice_var = tk.StringVar(value="晓晓 - 女声（推荐）")
voice_combo = ttk.Combobox(control, textvariable=voice_var, values=list(voices.keys()), state="readonly", width=42)
voice_combo.grid(row=0, column=1, padx=10, sticky="w")

# 语速调节
ttk.Label(control, text="语速调整：").grid(row=1, column=0, sticky="w", pady=6)
rate_var = tk.StringVar(value="+0%")
rate_combo = ttk.Combobox(control, textvariable=rate_var, 
                         values=["-40%", "-30%", "-20%", "-10%", "+0%", "+10%", "+20%", "+30%", "+40%"], width=15)
rate_combo.grid(row=1, column=1, padx=10, sticky="w")

# 输出路径
ttk.Label(control, text="保存为 MP3：").grid(row=2, column=0, sticky="w", pady=6)
output_var = tk.StringVar()
output_entry = ttk.Entry(control, textvariable=output_var, width=55)
output_entry.grid(row=2, column=1, padx=10, sticky="ew")

def browse():
    path = filedialog.asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("MP3 文件", "*.mp3")],
        initialfile="晓晓朗读.mp3"
    )
    if path:
        output_var.set(path)

ttk.Button(control, text="浏览...", command=browse).grid(row=2, column=2, padx=5)

status_label = ttk.Label(root, text="就绪", foreground="gray")
status_label.pack(pady=10)

# ==================== 生成函数（带用时统计） ====================
def generate():
    text = text_area.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("警告", "请输入文本！")
        return

    selected_voice = voices[voice_var.get()]
    output_path = output_var.get().strip()
    if not output_path:
        messagebox.showwarning("警告", "请选择保存路径！")
        return

    # 禁用按钮
    speak_btn.config(state="disabled")
    save_btn.config(state="disabled")
    status_label.config(text="正在生成语音... 请耐心等待")

    start_time = time.time()   # ← 记录开始时间

    def task():
        try:
            communicate = edge_tts.Communicate(
                text=text, 
                voice=selected_voice,
                rate=rate_var.get()
            )
            asyncio.run(communicate.save(output_path))
            
            end_time = time.time()
            used_time = end_time - start_time
            used_str = f"{used_time:.2f} 秒"

            if os.path.exists(output_path):
                msg = f"转换成功！\n\n文件已保存：\n{output_path}\n\n本次转换用时：{used_str}"
                root.after(0, lambda: messagebox.showinfo("成功", msg))
                root.after(0, lambda: status_label.config(text=f"生成完成 - 用时 {used_str}"))
            else:
                root.after(0, lambda: messagebox.showerror("错误", "文件保存失败"))
                root.after(0, lambda: status_label.config(text="保存失败"))
                
        except Exception as e:
            end_time = time.time()
            used_time = end_time - start_time
            root.after(0, lambda: messagebox.showerror("错误", 
                f"生成失败：\n{str(e)}\n\n本次尝试用时：{used_time:.2f} 秒\n请检查网络连接"))
            root.after(0, lambda: status_label.config(text="生成失败"))
        finally:
            # 恢复按钮
            root.after(0, lambda: speak_btn.config(state="normal"))
            root.after(0, lambda: save_btn.config(state="normal"))

    threading.Thread(target=task, daemon=True).start()

# 按钮区
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=15)

speak_btn = ttk.Button(btn_frame, text="▶ 仅朗读（不保存）", command=generate)
speak_btn.pack(side="left", padx=20)

save_btn = ttk.Button(btn_frame, text="💾 生成并保存 MP3", command=generate)
save_btn.pack(side="left", padx=20)

tip = ttk.Label(root, 
    text="提示：\n"
         "• 晓晓声音自然度很高，支持较长文本\n"
         "• 长文本转换时间会较长，取决于文本长度和网络速度\n"
         "• 生成完成后会弹出用时统计",
    foreground="blue", justify="left")
tip.pack(pady=8, anchor="w", padx=25)

root.mainloop()