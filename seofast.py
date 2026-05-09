import requests
import json
import time
import random
import hashlib
from datetime import datetime

class SeoFastBot:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://seo-fast.bz/webapp/ajax/ajax_views.php"
        
        print("=== SEO-FAST.BZ AUTO BOT ===")
        self.email = input("[?] Email: ").strip()
        self.password = input("[?] Password: ").strip()
        
        # Sekarang bisa ganti device_id sesuka hati!
        self.id_device = "secure_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        self.hash_ajax = None
        
        # Hitung App Token secara dinamis
        package_name = "com.example.seofast"
        salt = "seo_fast_SFk1gR5h5DGH"
        string_to_hash = f"{self.id_device}:{package_name}:{salt}"
        self.app_token = hashlib.sha256(string_to_hash.encode()).hexdigest()
        
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; WayDroid x86_64 Device Build/TQ3A.230901.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Safari/537.36 SeoFast-App/1.0",
            'Accept': "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            'X-Requested-With': "XMLHttpRequest",
            'X-App-Version': "1.1.0",
            'X-App-Token': self.app_token,
            'X-Device-Id': self.id_device,
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Origin': "https://seo-fast.bz",
            'Referer': "https://seo-fast.bz/webapp/?pg=login",
            'Accept-Language': "en-US,en;q=0.9",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty"
        }

        # Template data_json untuk complete_task (diambil dari HAR)
        self.device_info_template = {
            "device_id": self.id_device,
            "device_type": "secure_device",
            "is_emulator": False,
            "is_secure": True,
            "emulator_type": "",
            "emulator_details": {
                "build_properties": False, "hardware": False, "files": False, "memu": False,
                "bluestacks": False, "nox": False, "genymotion": False, "google_emulator": False,
                "masking_detected": True
            },
            "google_email": "ceeskamu@gmail.com",
            "hardware": {
                "brand": "waydroid", "model": "WayDroid x86_64 Device", "device": "waydroid_x86_64",
                "hardware": "unknown", "manufacturer": "Waydroid", "product": "lineage_waydroid_x86_64",
                "board": "unknown"
            },
            "os": {"sdk_int": 33, "release": "13", "incremental": "eng.aleast.20260403.113748"},
            "display": {"width_px": 1920, "height_px": 965, "density_dpi": 180, "density": 1.125},
            "locale": {"language": "en", "country": "US", "variant": ""},
            "timezone": "Asia/Jakarta",
            "extra": {
                "fingerprint": "waydroid/lineage_waydroid_x86_64/waydroid_x86_64:13/TQ3A.230901.001/eng.aleast.20260403.113748:userdebug/test-keys",
                "tags": "test-keys", "type": "userdebug", "user": "aleasto", "host": "zero"
            },
            "masking_detected": True,
            "masking_evidence": {}
        }

    def login(self):
        print("[*] Mencoba login otomatis...")
        try:
            # 1. Ambil hash awal dari halaman login
            headers = self.headers.copy()
            res_page = self.session.get("https://seo-fast.bz/webapp/?pg=login", headers=headers)
            import re
            match = re.search(r"var hash_ajax = '(.*?)';", res_page.text)
            if not match:
                print("[-] Gagal mengambil hash login.")
                return False
            
            self.hash_ajax = match.group(1)
            
            # 2. Kirim request login
            login_url = "https://seo-fast.bz/webapp/ajax/ajax_login.php"
            payload = {
                "login": self.email,
                "password": self.password,
                "hash": self.hash_ajax,
                "ajax_func": "login"
            }
            
            # Login uses form-urlencoded
            headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
            res_login = self.session.post(login_url, data=payload, headers=headers)
            
            if "location.replace('?pg=job')" in res_login.text:
                print("[+] Login Berhasil!")
                # Ambil hash baru dari halaman job
                self.get_session_info()
                return True
            else:
                print(f"[-] Login Gagal: {res_login.text}")
        except Exception as e:
            print(f"[-] Error saat login: {e}")
        return False

    def get_session_info(self):
        print("[*] Memperbarui hash_ajax untuk sesi tugas...")
        headers = self.headers.copy()
        headers['Content-Type'] = "text/html" # Biasanya GET page gak butuh specific Content-Type tapi buat amannya
        try:
            res = self.session.get("https://seo-fast.bz/webapp/?pg=job", headers=headers)
            import re
            match = re.search(r"var hash_ajax = '(.*?)';", res.text)
            if match:
                self.hash_ajax = match.group(1)
                print(f"[+] Hash Ajax terbaru: {self.hash_ajax}")
                # Update base headers for future JSON requests
                self.headers['Content-Type'] = "application/json"
                return True
        except: pass
        return False

    def get_task(self):
        print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] Mengambil tugas baru...")
        payload = {
            "ajax_func": "get_task",
            "id_device": self.id_device,
            "hash_ajax": self.hash_ajax
        }
        try:
            res = self.session.post(self.base_url, json=payload, headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("status"):
                    return data
                else:
                    print(f"[!] Tidak ada tugas tersedia atau error: {res.text}")
            else:
                print(f"[-] Gagal ambil tugas ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"[-] Error get_task: {e}")
        return None

    def complete_task(self, id_status):
        print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] Menyelesaikan tugas ID: {id_status}...")
        
        # Update timestamp di data_json
        device_info = self.device_info_template.copy()
        device_info["timestamp"] = int(time.time() * 1000)
        
        payload = {
            "ajax_func": "complete_task",
            "id_status": str(id_status),
            "id_device": self.id_device,
            "data_json": json.dumps(device_info),
            "hash_ajax": self.hash_ajax
        }
        
        try:
            res = self.session.post(self.base_url, json=payload, headers=self.headers)
            # print(res.json())
            if res.status_code == 200:
                data = res.json()
                balance = data.get('balance', 'N/A')
                earned = data.get('earned', 'N/A')
                print(f"[+] Tugas selesai! Saldo: {balance} RUB (Total Earned: {earned})")
                return True
            else:
                print(f"[-] Gagal selesaikan tugas ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"[-] Error complete_task: {e}")
        return False

    def update_data(self):
        print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] Mengirim up_data awal...")
        url = "https://seo-fast.bz/webapp/ajax/ajax_data.php"
        
        device_info = self.device_info_template.copy()
        device_info["timestamp"] = int(time.time() * 1000)
        
        payload = {
            "ajax_func": "up_data",
            "hash_ajax": self.hash_ajax,
            "id_device": self.id_device,
            "email": "ceeskamu@gmail.com",
            "os_version": "13",
            "screen_resolution": "1920x965",
            "locale_language": "en",
            "locale_country": "US",
            "data_json": json.dumps(device_info)
        }
        
        try:
            res = self.session.post(url, json=payload, headers=self.headers)
            print(f"[+] Up Data Response: {res.text}")
            return True
        except Exception as e:
            print(f"[-] Error update_data: {e}")
        return False

    def run(self):
        print("="*40)
        print("   SEO-FAST.BZ AUTO BOT STARTED")
        print("="*40)
        
        if not self.login():
            return
            
        # Kirim update data sekali di awal
        self.update_data()
        
        while True:
            task = self.get_task()
            if task:
                id_status = task.get("id_status")
                # print(task)
                timer = int(task.get("timer", 15))
                url = task.get("url")
                
                print(f"[i] Menjalankan: {url}")
                print(f"[i] Menunggu timer {timer} detik: ", end="", flush=True)
                
                # Countdown timer
                for i in range(timer + 1, 0, -1):
                    print(f"{i}..", end="\r", flush=True)
                    time.sleep(1)
                print(" Done!")
                
                self.complete_task(id_status)
                
                # Jeda antar tugas
                # delay = random.randint(5, 10)
                # print(f"[*] Jeda {delay} detik...")
                # time.sleep(delay)
            else:
                # Jika tidak ada tugas, tunggu agak lama
                print("[*] Menunggu 30 detik sebelum mencoba lagi...")
                time.sleep(30)

if __name__ == "__main__":
    bot = SeoFastBot()
    bot.run()
