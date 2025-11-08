#!/usr/bin/env python3
# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import psutil
import socket
import time
import pyperclip
import requests
import sys

BASE_DIR = os.path.dirname(__file__)
SERVER_PY = os.path.join(BASE_DIR, "server.py")
SITES_DIR = os.path.join(BASE_DIR, "sites")
PUBLIC_URL = ""
PUBLIC_IP = "Unknown"

server_proc = None
tunnel_proc = None

# === DİL SÖZLÜĞÜ ===
LANGUAGES = {
    "tr": {
        "title": "Web Server Manager",
        "file_label": "Dosya:",
        "select": "Seç",
        "port_label": "Port:",
        "find_port": "Boş Port Bul",
        "subdomain_label": "Subdomain:",
        "public_check": "Public Yap",
        "keep_tunnel": "Hep Dışarı Açık",
        "start_server": "Sunucuyu Aç",
        "stop_server": "Sunucuyu Kapat",
        "copy_url": "URL Kopyala",
        "status": "Durum: Kapalı",
        "system_monitor": "Sistem İzleme",
        "cpu": "CPU",
        "ram": "RAM",
        "html_storage": "HTML Depolama",
        "last_update": "Son",
        "console": "Konsol (Canlı Log)",
        "tunnel_ip": "Tunnel Password ve Public IP",
        "close_app": "Uygulamayı Kapat",
        "footer": "F11: Tam Ekran | ESC: Çık | URL Kopyala: Bağlantıyı panoya koyar",
        "ready": "Hazır. Dosya seçin ve 'Sunucuyu Aç' tıklayın.",
        "selected": "Seçildi:",
        "port_found": "Boş port bulundu:",
        "server_started": "Sunucu açıldı:",
        "server_closed": "Sunucu kapatıldı.",
        "tunnel_closed": "Tunnel kapatıldı.",
        "copied": "URL panoya kopyalandı:",
        "no_url": "Henüz URL yok.",
        "exit_confirm": "Uygulamayı kapatmak istiyor musunuz?",
    },
    "en": {
        "title": "Web Server Manager",
        "file_label": "File:",
        "select": "Select",
        "port_label": "Port:",
        "find_port": "Find Free Port",
        "subdomain_label": "Subdomain:",
        "public_check": "Make Public",
        "keep_tunnel": "Always Public",
        "start_server": "Start Server",
        "stop_server": "Stop Server",
        "copy_url": "Copy URL",
        "status": "Status: Offline",
        "system_monitor": "System Monitor",
        "cpu": "CPU",
        "ram": "RAM",
        "html_storage": "HTML Storage",
        "last_update": "Last",
        "console": "Console (Live Log)",
        "tunnel_ip": "Tunnel Password & Public IP",
        "close_app": "Close App",
        "footer": "F11: Fullscreen | ESC: Exit | Copy URL: Copies to clipboard",
        "ready": "Ready. Select a file and click 'Start Server'.",
        "selected": "Selected:",
        "port_found": "Free port found:",
        "server_started": "Server started:",
        "server_closed": "Server stopped.",
        "tunnel_closed": "Tunnel stopped.",
        "copied": "URL copied to clipboard:",
        "no_url": "No URL yet.",
        "exit_confirm": "Do you want to close the app?",
    }
}

# Varsayılan dil
current_lang = "tr"
lang = LANGUAGES[current_lang]

def get_free_port():
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "Unknown"

class WebServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title(lang["title"])
        self.root.geometry("620x780")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        icon_path = os.path.join(BASE_DIR, "icon.png")
        if os.path.exists(icon_path):
            try: self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            except: pass

        self.create_widgets()
        self.update_system()
        self.update_status()
        self.update_storage()

    def create_widgets(self):
        # Dil Seçimi
        lang_frame = tk.Frame(self.root, bg="#f0f0f0")
        lang_frame.pack(pady=5)
        tk.Label(lang_frame, text="Language:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value="tr")
        ttk.Combobox(lang_frame, textvariable=self.lang_var, values=["tr", "en"], width=5, state="readonly").pack(side=tk.LEFT, padx=5)
        self.lang_var.trace("w", self.change_language)

        # Başlık
        self.title_label = tk.Label(self.root, text=lang["title"], font=("Arial", 20, "bold"), fg="#2c3e50", bg="#f0f0f0")
        self.title_label.pack(pady=15)

        # Dosya Seç
        file_frame = tk.Frame(self.root, bg="#f0f0f0")
        file_frame.pack(pady=8)
        tk.Label(file_frame, text=lang["file_label"], bg="#f0f0f0").pack(side=tk.LEFT)
        self.file_var = tk.StringVar(value="Seçilmedi")
        tk.Label(file_frame, textvariable=self.file_var, width=30, relief="sunken", bg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text=lang["select"], bg="#3498db", fg="white", command=self.select_file).pack(side=tk.LEFT)

        # Port
        port_frame = tk.Frame(self.root, bg="#f0f0f0")
        port_frame.pack(pady=8)
        tk.Label(port_frame, text=lang["port_label"], bg="#f0f0f0").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8080")
        tk.Entry(port_frame, textvariable=self.port_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(port_frame, text=lang["find_port"], bg="#95a5a6", fg="white", command=self.find_free_port).pack(side=tk.LEFT)

        # Public + Hep Açık
        public_frame = tk.Frame(self.root, bg="#f0f0f0")
        public_frame.pack(pady=8)
        tk.Label(public_frame, text=lang["subdomain_label"], bg="#f0f0f0").pack(side=tk.LEFT)
        self.sub_var = tk.StringVar(value="mysite")
        tk.Entry(public_frame, textvariable=self.sub_var, width=15).pack(side=tk.LEFT, padx=5)
        tk.Label(public_frame, text=".loca.lt", bg="#f0f0f0").pack(side=tk.LEFT)
        self.public_check = tk.BooleanVar(value=False)
        tk.Checkbutton(public_frame, text=lang["public_check"], variable=self.public_check, bg="#f0f0f0").pack(side=tk.LEFT, padx=8)
        self.keep_tunnel_check = tk.BooleanVar(value=False)
        tk.Checkbutton(public_frame, text=lang["keep_tunnel"], variable=self.keep_tunnel_check, bg="#f0f0f0").pack(side=tk.LEFT)

        # Butonlar
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text=lang["start_server"], bg="#27ae60", fg="white", width=14, command=self.start_server).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text=lang["stop_server"], bg="#e74c3c", fg="white", width=14, command=self.stop_server).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text=lang["copy_url"], bg="#e67e22", fg="white", width=14, command=self.copy_url).pack(side=tk.LEFT, padx=4)

        # Durum
        self.status_var = tk.StringVar(value=lang["status"])
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10, "bold"), fg="red", bg="#f0f0f0")
        self.status_label.pack(pady=5)

        # Sistem İzleme
        sys_frame = tk.LabelFrame(self.root, text=lang["system_monitor"], font=("Arial", 12, "bold"), padx=15, pady=10, bg="#f0f0f0")
        sys_frame.pack(fill="x", padx=40, pady=8)
        self.cpu_label = tk.Label(sys_frame, text=f"{lang['cpu']}: 0.0%", bg="#f0f0f0"); self.cpu_label.pack(anchor="w")
        self.cpu_bar = ttk.Progressbar(sys_frame, length=500); self.cpu_bar.pack(pady=2, fill="x")
        self.ram_label = tk.Label(sys_frame, text=f"{lang['ram']}: 0.0%", bg="#f0f0f0"); self.ram_label.pack(anchor="w")
        self.ram_bar = ttk.Progressbar(sys_frame, length=500); self.ram_bar.pack(pady=2, fill="x")
        self.storage_label = tk.Label(sys_frame, text=f"{lang['html_storage']}: 0.000 GB", bg="#f0f0f0"); self.storage_label.pack(anchor="w")
        self.time_label = tk.Label(sys_frame, text=f"{lang['last_update']}: --:--:--", bg="#f0f0f0"); self.time_label.pack(anchor="w")

        # Konsol
        log_frame = tk.LabelFrame(self.root, text=lang["console"], font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f0f0")
        log_frame.pack(fill="both", expand=True, padx=40, pady=8)
        self.log_text = tk.Text(log_frame, height=8, bg="black", fg="#00ff00", font=("Courier", 10))
        self.log_text.pack(fill="both", expand=True)
        self.log(lang["ready"])

        # Tunnel IP
        self.ip_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.ip_frame.pack(pady=5)
        self.ip_label = tk.Label(self.ip_frame, text=f"{lang['tunnel_ip']}: Unknown", font=("Courier", 10), fg="#e67e22", bg="#f0f0f0")
        self.ip_label.pack()

        # Kapatma
        close_frame = tk.Frame(self.root, bg="#f0f0f0")
        close_frame.pack(pady=8)
        tk.Button(close_frame, text=lang["close_app"], bg="#c0392b", fg="white", width=20, command=self.on_closing).pack()

        # Footer
        self.footer_label = tk.Label(self.root, text=lang["footer"], font=("Arial", 8), fg="gray", bg="#f0f0f0")
        self.footer_label.pack(side=tk.BOTTOM, pady=10)

    def change_language(self, *args):
        global current_lang, lang
        current_lang = self.lang_var.get()
        lang = LANGUAGES[current_lang]
        self.update_ui_texts()

    def update_ui_texts(self):
        self.root.title(lang["title"])
        self.title_label.config(text=lang["title"])
        # Tüm widget'ları güncelle
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    self.update_widget_text(child)
            else:
                self.update_widget_text(widget)
        self.log_text.delete(1.0, tk.END)
        self.log(lang["ready"])
        self.status_var.set(lang["status"] if not server_proc else "Durum: Çalışıyor" if current_lang == "tr" else "Status: Online")

    def update_widget_text(self, widget):
        if isinstance(widget, tk.Label) and widget.cget("text").startswith(("Dosya:", "Port:", "Subdomain:", "CPU", "RAM", "HTML", "Son", "Tunnel")):
            pass  # dinamik
        elif isinstance(widget, tk.Button):
            text = widget.cget("text")
            if text in ["Seç", "Select"]: widget.config(text=lang["select"])
            elif text in ["Boş Port Bul", "Find Free Port"]: widget.config(text=lang["find_port"])
            elif text in ["Sunucuyu Aç", "Start Server"]: widget.config(text=lang["start_server"])
            elif text in ["Sunucuyu Kapat", "Stop Server"]: widget.config(text=lang["stop_server"])
            elif text in ["URL Kopyala", "Copy URL"]: widget.config(text=lang["copy_url"])
            elif text in ["Uygulamayı Kapat", "Close App"]: widget.config(text=lang["close_app"])
        elif isinstance(widget, tk.Checkbutton):
            text = widget.cget("text")
            if text in ["Public Yap", "Make Public"]: widget.config(text=lang["public_check"])
            elif text in ["Hep Dışarı Açık", "Always Public"]: widget.config(text=lang["keep_tunnel"])
        elif isinstance(widget, tk.LabelFrame):
            widget.config(text=lang["system_monitor"] if "Sistem" in widget.cget("text") else lang["console"])

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        if path:
            self.file_var.set(os.path.basename(path))
            self.selected_file = path
            self.log(f"{lang['selected']} {os.path.basename(path)}")

    def find_free_port(self):
        port = get_free_port()
        self.port_var.set(str(port))
        self.log(f"{lang['port_found']} {port}")

    def start_server(self):
        global server_proc, tunnel_proc, PUBLIC_URL, PUBLIC_IP
        if server_proc and server_proc.poll() is None:
            messagebox.showwarning("Error", lang["start_server"].replace("Sunucuyu Aç", "Server already running") if current_lang == "tr" else "Server already running!")
            return
        if not hasattr(self, 'selected_file'):
            messagebox.showwarning("Error", "Please select a file!" if current_lang == "en" else "Lütfen dosya seçin!")
            return

        port = int(self.port_var.get())
        os.makedirs(SITES_DIR, exist_ok=True)
        dest = os.path.join(SITES_DIR, "index.html")
        import shutil
        shutil.copy(self.selected_file, dest)

        cmd = [sys.executable, SERVER_PY, str(port)]
        server_proc = subprocess.Popen(cmd, cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def read_logs():
            for line in server_proc.stdout:
                self.log(line.strip())
            for line in server_proc.stderr:
                self.log(f"ERROR: {line.strip()}")

        threading.Thread(target=read_logs, daemon=True).start()

        if self.public_check.get():
            subdomain = self.sub_var.get().strip()
            def start_tunnel():
                global tunnel_proc, PUBLIC_URL
                time.sleep(2)
                tunnel_cmd = ["lt", "--port", str(port), "--subdomain", subdomain]
                if self.keep_tunnel_check.get():
                    tunnel_cmd += ["--local-host", "localhost"]
                tunnel_proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.PIPE, text=True, cwd=BASE_DIR)
                for line in tunnel_proc.stdout:
                    line = line.strip()
                    self.log(line)
                    if "your url is:" in line.lower():
                        url = line.split("your url is:")[-1].strip()
                        PUBLIC_URL = url
                        self.update_ip_display()
            threading.Thread(target=start_tunnel, daemon=True).start()
        else:
            PUBLIC_URL = f"http://localhost:{port}"

        self.status_var.set("Durum: Çalışıyor" if current_lang == "tr" else "Status: Online")
        self.status_label.config(fg="green")
        self.log(f"{lang['server_started']} {PUBLIC_URL}")

        PUBLIC_IP = get_public_ip()
        self.update_ip_display()

    def stop_server(self):
        global server_proc, tunnel_proc
        if server_proc and server_proc.poll() is None:
            server_proc.terminate()
            self.log(lang["server_closed"])
        if tunnel_proc and tunnel_proc.poll() is None and not self.keep_tunnel_check.get():
            tunnel_proc.terminate()
            self.log(lang["tunnel_closed"])
        if not (server_proc and server_proc.poll() is None):
            self.status_var.set(lang["status"])
            self.status_label.config(fg="red")

    def copy_url(self):
        if PUBLIC_URL:
            pyperclip.copy(PUBLIC_URL)
            messagebox.showinfo("Copied", f"{lang['copied']}\n{PUBLIC_URL}")
        else:
            messagebox.showwarning("Error", lang["no_url"])

    def update_ip_display(self):
        global PUBLIC_IP
        self.ip_label.config(text=f"{lang['tunnel_ip']}: {PUBLIC_IP}")

    def update_system(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_label.config(text=f"{lang['cpu']}: {cpu:.1f}%")
        self.cpu_bar['value'] = cpu
        self.ram_label.config(text=f"{lang['ram']}: {ram:.1f}%")
        self.ram_bar['value'] = ram
        self.time_label.config(text=f"{lang['last_update']}: {time.strftime('%H:%M:%S')}")
        self.root.after(1000, self.update_system)

    def update_storage(self):
        total = 0
        if os.path.exists(SITES_DIR):
            for root, dirs, files in os.walk(SITES_DIR):
                for f in files:
                    if f.endswith(".html"):
                        fp = os.path.join(root, f)
                        total += os.path.getsize(fp)
        gb = total / (1024**3)
        self.storage_label.config(text=f"{lang['html_storage']}: {gb:.3f} GB")
        self.root.after(5000, self.update_storage)

    def update_status(self):
        if server_proc and server_proc.poll() is None:
            self.status_var.set("Durum: Çalışıyor" if current_lang == "tr" else "Status: Online")
            self.status_label.config(fg="green")
        else:
            self.status_var.set(lang["status"])
            self.status_label.config(fg="red")
        self.root.after(1000, self.update_status)

    def on_closing(self):
        if messagebox.askokcancel("Exit", lang["exit_confirm"]):
            self.stop_server()
            if tunnel_proc and tunnel_proc.poll() is None:
                tunnel_proc.terminate()
            self.root.quit()
            self.root.destroy()
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebServerManager(root)
    root.mainloop()
