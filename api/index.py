from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import time

app = Flask(__name__)

# Global session and data
# Note: On Vercel, global variables are not persistent across different invocations.
bot_session = requests.Session()
bot_data = {
    "hash_ajax": None,
    "headers": {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; WayDroid x86_64 Device Build/TQ3A.230901.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Safari/537.36 SeoTask-App/1.0",
        'X-App-Token': "fb00fe7980cc43364602105bf4296e455f5a9e818489df3935c8bb92edacf5f0",
        'X-App-Version': "1.3.3",
        'X-Device-Id': "pro_2935e3aeab9ff72f",
        'X-Requested-With': "XMLHttpRequest",
        'Content-Type': "application/json; charset=utf-8",
    }
}

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
                <input type="email" name="email" value="ceeskamu@gmail.com" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" value="OXb8V0n" required>
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
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    res = bot_session.get("https://seo-task.com/webphone/?pg=login", headers=bot_data['headers'])
    bs = BeautifulSoup(res.text, 'html.parser')
    c1_style = bs.find("div", class_="out-capcha-img-block").get("style")
    c1_base64 = re.search(r'base64,(.*?)\)', c1_style).group(1)
    c2_div = bs.find("div", class_="out-capcha-title-img")
    c2_base64 = re.search(r'base64,(.*?)\)', c2_div.get("style")).group(1) if c2_div else ""
    bot_data['hash_initial'] = bs.find('input', {'name': 'hash'}).get('value')
    bot_data['captcha_labels'] = bs.find_all("label", class_="out-capcha-lab")
    return render_template_string(HTML_TEMPLATE, c1=c1_base64, c2=c2_base64)

@app.route('/login', methods=['POST'])
def do_login():
    email, password, posisi = request.form.get('email'), request.form.get('password'), request.form.get('captcha_pos')
    login_payload = [('login', email), ('password', password), ('hash', bot_data['hash_initial']), ('ajax_func', "login")]
    for x in posisi.split(","):
        idx = int(x.strip()) - 1
        login_payload.append(('capcha[]', bot_data['captcha_labels'][idx].find("input").get("value")))
    
    login_headers = bot_data['headers'].copy()
    login_headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
    res_login = bot_session.post("https://seo-task.com/webphone/ajax/ajax_login.php", data=login_payload, headers=login_headers)
    
    if "pg=job" in res_login.text:
        res_dash = bot_session.get("https://seo-task.com/webphone/?pg=job", headers=bot_data['headers'])
        script_tag = BeautifulSoup(res_dash.text, 'html.parser').find('script', string=re.compile('hash_ajax'))
        bot_data['hash_ajax'] = re.search(r"hash_ajax = '(.*?)';", script_tag.string).group(1)
        return "<h1>Login Berhasil!</h1><p>Buka <b><a href='/selesaikantugas'>/selesaikantugas</a></b>.</p>"
    return "<h1>Gagal Login</h1>"

@app.route('/selesaikantugas')
def complete_task():
    if not bot_data.get('hash_ajax'): return jsonify({"status": False, "error": "Login dulu"})
    task_url = "https://seo-task.com/webphone/ajax/ajax_views.php"
    task_req = bot_session.post(task_url, headers=bot_data['headers'], json={"ajax_func": "get_task", "hash_ajax": bot_data['hash_ajax']})
    task = task_req.json()
    if task.get('status'):
        time.sleep(int(task.get('timer', 10)) + 2)
        comp_payload = {"ajax_func": "complete_task", "id_status": str(task['id_status']), "hash_ajax": bot_data['hash_ajax'], "data_json": json.dumps({"timestamp": int(time.time()*1000), "device_id": "pro_2935e3aeab9ff72f"})}
        comp_res = bot_session.post(task_url, headers=bot_data['headers'], json=comp_payload)
        return jsonify(comp_res.json())
    return jsonify({"status": "Gagal", "message": task.get('mess', 'Tidak ada tugas.')})

if __name__ == '__main__':
    app.run()
