import requests
import base64
import json
import time
import sys

def start_bot():
    print("="*40)
    print("      SEOTASK CLI BOT RUNNER")
    print("="*40)
    
    # Input data base64 dari user
    state_raw = input("\n[?] Masukkan Data Base64 (dari Dashboard/Login): ").strip()
    
    try:
        # Decode data
        state = json.loads(base64.b64decode(state_raw).decode())
        device = state['device']
        phpsessid = state['phpsessid']
        hash_ajax = state['hash_ajax']
        
        print(f"\n[+] Data Valid!")
        print(f"    Device ID : {device['device_id']}")
        print(f"    Email     : {state.get('email', 'N/A')}")
        print(f"    PHPSESSID : {phpsessid[:10]}...")
        
        # Inisialisasi Session
        sess = requests.Session()
        sess.cookies.set("PHPSESSID", phpsessid)
        
        headers = {
            'User-Agent': device['user_agent'],
            'X-App-Token': device['app_token'],
            'X-Device-Id': device['device_id'],
            'X-Requested-With': "XMLHttpRequest",
            'Content-Type': "application/json; charset=utf-8",
            'Accept-Language': "en-US,en;q=0.9"
        }

        print("\n[!] Menjalankan Bot Otomatis... (Ctrl+C untuk berhenti)")
        
        while True:
            try:
                # 1. Ambil Tugas
                task_url = "https://seo-task.com/webphone/ajax/ajax_views.php"
                res = sess.post(task_url, headers=headers, json={"ajax_func": "get_task", "hash_ajax": hash_ajax})
                
                try:
                    task = res.json()
                except:
                    print(f"[-] Gagal parse JSON. Response: {res.text}")
                    time.sleep(10)
                    continue

                if task.get('status'):
                    id_status = task['id_status']
                    timer = int(task.get('timer', 10))
                    
                    print(f"\n[+] Tugas Ditemukan! ID: {id_status}")
                    print(f"    Menonton selama {timer} detik...")
                    
                    # 2. Simulasi Menonton
                    for i in range(timer + 2, 0, -1):
                        print(f"\r    Sisa waktu: {i} detik... ", end="", flush=True)
                        time.sleep(1)
                    print("\r    Waktu selesai! Mengirim konfirmasi...          ", flush=True)

                    # 3. Selesaikan Tugas
                    comp_payload = {
                        "ajax_func": "complete_task",
                        "id_status": str(id_status),
                        "hash_ajax": hash_ajax,
                        "data_json": json.dumps({
                            "timestamp": int(time.time()*1000), 
                            "device_id": device['device_id']
                        })
                    }
                    comp_res = sess.post(task_url, headers=headers, json=comp_payload)
                    
                    try:
                        result = comp_res.json()
                        if result.get('status'):
                            print(f"    [SUCCESS] Berhasil! Saldo: {result.get('balance')} RUB")
                        else:
                            print(f"    [FAILED] Gagal: {result.get('mess')}")
                    except:
                        print(f"    [!] Error response: {comp_res.text}")
                    
                    time.sleep(3) # Jeda antar tugas
                
                else:
                    mess = task.get('mess', 'Tidak ada tugas.')
                    print(f"\r[-] {mess} Mencoba lagi dalam 15 detik...", end="", flush=True)
                    time.sleep(15)

            except requests.exceptions.RequestException as e:
                print(f"\n[!] Koneksi Error: {e}")
                time.sleep(10)
                
    except Exception as e:
        print(f"\n[!] Terjadi Kesalahan: {e}")
        print("[*] Pastikan data Base64 yang Anda masukkan benar.")

if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n\n[!] Bot dihentikan oleh user. Sampai jumpa!")
        sys.exit(0)
