# server.py
import http.server
import socketserver
import os
import sys
import threading
import signal
import logging

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

if len(sys.argv) < 2:
    print("Kullanım: python server.py <port>")
    sys.exit(1)

try:
    PORT = int(sys.argv[1])
except ValueError:
    print("Hata: Port bir sayı olmalı!")
    sys.exit(1)

SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")

# sites/ klasörü yoksa oluştur
os.makedirs(SITES_DIR, exist_ok=True)

# index.html yoksa varsayılan oluştur
index_path = os.path.join(SITES_DIR, "index.html")
if not os.path.exists(index_path):
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html><head><title>Hoş Geldiniz</title>
<style>body{font-family:Arial;text-align:center;margin-top:10%;}</style>
</head><body>
<h1>Web Sunucusu Çalışıyor!</h1>
<p>Sitenizi <code>sites/</code> klasörüne koyun.</p>
</body></html>""")
    logging.info("Varsayılan index.html oluşturuldu.")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITES_DIR, **kwargs)

    def log_message(self, format, *args):
        # Logları konsola ve dosyaya yaz
        logging.info(f"{self.client_address[0]} - {format % args}")

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_HEAD(self):
        return super().do_HEAD()

def signal_handler(signum, frame):
    logging.info("Sunucu kapatılıyor...")
    sys.exit(0)

# SIGINT (Ctrl+C) ve SIGTERM yakala
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_server():
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        host = socket.gethostbyname(socket.gethostname())
        logging.info(f"Sunucu çalışıyor:")
        logging.info(f"   Local: http://localhost:{PORT}")
        logging.info(f"   Ağ:    http://{host}:{PORT}")
        logging.info(f"   Dizin: {os.path.abspath(SITES_DIR)}")
        print(f"[+] Sunucu çalışıyor: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            logging.info("Sunucu durduruldu.")
            httpd.server_close()

if __name__ == "__main__":
    run_server()