from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import time

app = Flask(__name__)

import uuid
import random
import hashlib

app = Flask(__name__)

def generate_random_device():
    # Sekarang kita bisa menggunakan ID acak karena sudah tahu rumusnya!
    device_id = f"secure_{uuid.uuid4().hex[:16]}"
    package_name = "com.example.videoload"
    salt = "seo_task_ge6fdgvskt"
    
    # Hitung X-App-Token sesuai algoritma aplikasi asli
    string_to_hash = f"{device_id}:{package_name}:{salt}"
    app_token = hashlib.sha256(string_to_hash.encode()).hexdigest()
    
    android_versions = ["11", "12", "13"]
    ver = random.choice(android_versions)
    build = f"TQ3A.{random.randint(230000, 230999)}.001"
    ua = f"Mozilla/5.0 (Linux; Android {ver}; WayDroid x86_64 Device Build/{build}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Safari/537.36 SeoTask-App/1.0"
    
    return {
        "device_id": device_id,
        "user_agent": ua,
        "app_token": app_token,
        "app_version": "1.3.3"
    }

# Temporary store for initial session before it's bundled into the "data" param
# No more global temp_sessions for Vercel

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SeoTask Bot Vercel</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #6366f1; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }
        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        }
        .container {
            background: var(--card);
            padding: 2.5rem;
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 2rem; font-weight: 600; }
        h1 span { color: var(--primary); }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: #94a3b8; font-size: 0.9rem; }
        input {
            width: 100%; padding: 0.8rem; background: #0f172a; border: 1px solid #334155;
            border-radius: 12px; color: white; box-sizing: border-box;
        }
        .captcha-box {
            display: flex; gap: 10px; margin: 1.5rem 0; background: #0f172a;
            padding: 1rem; border-radius: 16px; justify-content: center;
        }
        .captcha-box img { border-radius: 8px; border: 2px solid #334155; max-width: 45%; }
        button {
            width: 100%; padding: 1rem; background: var(--primary); color: white;
            border: none; border-radius: 12px; font-weight: 600; cursor: pointer;
        }
        .status { margin-top: 1.5rem; padding: 1rem; border-radius: 12px; background: #064e3b; color: #34d399; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SeoTask <span>Vercel</span></h1>
        <form action="/login" method="POST">
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" placeholder="Masukkan email Anda..." required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Masukkan password..." required>
            </div>
            <div class="captcha-box">
                <img src="data:image/jpeg;base64,{{ c2 }}" alt="Main Captcha">
                <img src="data:image/jpeg;base64,{{ c1 }}" alt="Question Captcha">
            </div>
            <div class="form-group">
                <label>Captcha Position</label>
                <input type="text" name="captcha_pos" placeholder="Masukkan posisi..." required>
            </div>
            <button type="submit">Start Session</button>
            <input type="hidden" name="state" value="{{ state }}">
        </form>
        <div style="margin-top: 2rem; text-align: center; font-size: 0.8rem; color: #64748b; border-top: 1px solid #334155; padding-top: 1rem;">
            Developed with ❤️ by <br>
            <span style="color: var(--primary); font-weight: 600; font-size: 1rem;">Muhamad Idris</span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    device = generate_random_device()
    bot_session = requests.Session()
    headers = {
        'User-Agent': device['user_agent'], 'X-App-Token': device['app_token'],
        'X-App-Version': device['app_version'], 'X-Device-Id': device['device_id'],
        'sec-ch-ua-platform': '"Android"', 'X-Requested-With': "XMLHttpRequest"
    }
    
    res = bot_session.get("https://seo-task.com/webphone/?pg=login", headers=headers)
    bs = BeautifulSoup(res.text, 'html.parser')
    
    try:
        c1_style = bs.find("div", class_="out-capcha-img-block").get("style")
        c1_base64 = re.search(r'base64,(.*?)\)', c1_style).group(1)
        c2_div = bs.find("div", class_="out-capcha-title-img")
        c2_base64 = re.search(r'base64,(.*?)\)', c2_div.get("style")).group(1) if c2_div else ""
        hash_init = bs.find('input', {'name': 'hash'}).get('value')
        
        # Bundle everything needed for login into a stateless string
        login_state = {
            "cookies": bot_session.cookies.get_dict(),
            "device": device,
            "hash_initial": hash_init,
            "captcha_labels": [str(l) for l in bs.find_all("label", class_="out-capcha-lab")]
        }
        state_encoded = base64.b64encode(json.dumps(login_state).encode()).decode()
        
        return render_template_string(HTML_TEMPLATE, c1=c1_base64, c2=c2_base64, state=state_encoded)
    except Exception as e:
        return f"Error loading login page: {e}. Refresh please."

@app.route('/login', methods=['POST'])
def do_login():
    state_raw = request.form.get('state')
    if not state_raw: return "State missing. Go back."
    
    data = json.loads(base64.b64decode(state_raw).decode())
    device = data['device']
    bot_session = requests.Session()
    bot_session.cookies.update(data['cookies'])
    
    email, password, posisi = request.form.get('email'), request.form.get('password'), request.form.get('captcha_pos')
    
    login_payload = [('login', email), ('password', password), ('hash', data['hash_initial']), ('ajax_func', "login")]
    for x in posisi.split(","):
        idx = int(x.strip()) - 1
        label_html = data['captcha_labels'][idx]
        val = BeautifulSoup(label_html, 'html.parser').find("input").get("value")
        login_payload.append(('capcha[]', val))
    
    headers = {
        'User-Agent': device['user_agent'], 'X-App-Token': device['app_token'],
        'X-Device-Id': device['device_id'], 'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'X-Requested-With': "XMLHttpRequest"
    }
    
    res_login = bot_session.post("https://seo-task.com/webphone/ajax/ajax_login.php", data=login_payload, headers=headers)
    
    if "pg=job" in res_login.text:
        res_dash = bot_session.get("https://seo-task.com/webphone/?pg=job", headers=headers)
        script_tag = BeautifulSoup(res_dash.text, 'html.parser').find('script', string=re.compile('hash_ajax'))
        hash_ajax = re.search(r"hash_ajax = '(.*?)';", script_tag.string).group(1)
        
        state = {"phpsessid": bot_session.cookies.get("PHPSESSID"), "hash_ajax": hash_ajax, "device": device, "email": email}
        state_encoded = base64.b64encode(json.dumps(state).encode()).decode()
        
        return f"""
        <div style="font-family: 'Outfit', sans-serif; background: #0f172a; color: white; padding: 2rem; border-radius: 20px; max-width: 500px; margin: 50px auto; border: 1px solid #334155;">
            <h1 style="color: #6366f1;">Login Berhasil! ✅</h1>
            <p>Identitas Device: <code>{device['device_id']}</code></p>
            <p>1. Klik link ini untuk mulai tugas:</p>
            <a href='/selesaikantugas?data={state_encoded}' style="display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 10px; font-weight: bold;">MULAI TUGAS</a>
            <p>2. Atau simpan data Base64 ini:</p>
            <textarea readonly style="width: 100%; height: 120px; background: #1e293b; color: #94a3b8; border: 1px solid #334155; border-radius: 10px; padding: 10px; font-family: monospace; font-size: 12px;">{state_encoded}</textarea>
            <br>
            <a href="/" style="color: #64748b; text-decoration: none; font-size: 14px;">← Kembali</a>
            <div style="margin-top: 2rem; text-align: center; font-size: 0.8rem; color: #64748b; border-top: 1px solid #334155; padding-top: 1rem;">
                Created by <span style="color: #6366f1; font-weight: 600;">Muhamad Idris</span>
            </div>
        </div>
        """
    return "<h1>Gagal Login</h1>"

@app.route('/selesaikantugas')
def complete_task():
    state_raw = request.args.get('data')
    if not state_raw: return jsonify({"error": "No data found"})
    try:
        state = json.loads(base64.b64decode(state_raw).decode())
        device = state['device']
        sess = requests.Session()
        sess.cookies.set("PHPSESSID", state['phpsessid'])
        headers = {'User-Agent': device['user_agent'], 'X-App-Token': device['app_token'], 'X-Device-Id': device['device_id'], 'X-Requested-With': "XMLHttpRequest", 'Content-Type': "application/json; charset=utf-8"}
        
        task_url = "https://seo-task.com/webphone/ajax/ajax_views.php"
        task_req = sess.post(task_url, headers=headers, json={"ajax_func": "get_task", "hash_ajax": state['hash_ajax']})
        task = task_req.json()
        
        if task.get('status'):
            time.sleep(int(task.get('timer', 10)) + 2)
            comp_payload = {"ajax_func": "complete_task", "id_status": str(task['id_status']), "hash_ajax": state['hash_ajax'], "data_json": json.dumps({"timestamp": int(time.time()*1000), "device_id": device['device_id']})}
            comp_res = sess.post(task_url, headers=headers, json=comp_payload)
            return jsonify({"status": "Success", "device": device['device_id'], "res": comp_res.json()})
        return jsonify({"status": "No Task", "mess": task.get('mess')})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
