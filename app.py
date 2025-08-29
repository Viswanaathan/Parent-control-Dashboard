from flask import Flask, request, render_template_string, redirect, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import threading, time, json, os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

usage_log = {}
blocked_domains = set()
focus_whitelist = set()
current_domain = None
start_time = None
focus_mode = False

BLOCKLIST_FILE = "blocked_domains.json"
USAGE_FILE = "usage_log.json"
WHITELIST_FILE = "focus_whitelist.json"
USAGE_THRESHOLD = 1800
DAILY_LIMIT = 3600

def load_blocklist():
    global blocked_domains
    if os.path.exists(BLOCKLIST_FILE):
        with open(BLOCKLIST_FILE, "r") as f:
            blocked_domains = set(json.load(f))

def save_blocklist():
    with open(BLOCKLIST_FILE, "w") as f:
        json.dump(list(blocked_domains), f)

def load_usage():
    global usage_log
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage_log = json.load(f)

def save_usage():
    with open(USAGE_FILE, "w") as f:
        json.dump(usage_log, f)

def load_whitelist():
    global focus_whitelist
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            focus_whitelist = set(json.load(f))
    else:
        focus_whitelist = {"khanacademy.org", "wikipedia.org", "nptel.ac.in"}

def save_whitelist():
    with open(WHITELIST_FILE, "w") as f:
        json.dump(list(focus_whitelist), f)

def normalize_domain(url):
    try:
        domain = urlparse(url).hostname or ""
        domain = domain.lower().replace("www.", "")
        parts = domain.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return domain
    except:
        return ""

def track_browser():
    global current_domain, start_time
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    while True:
        try:
            url = driver.current_url
            domain = normalize_domain(url)
            if domain != current_domain:
                if current_domain:
                    duration = int(time.time() - start_time)
                    usage_log[current_domain] = usage_log.get(current_domain, 0) + duration
                    save_usage()
                current_domain = domain
                start_time = time.time()
            if focus_mode and domain not in focus_whitelist:
                driver.execute_script("window.stop(); window.location.href='https://www.blocked.com';")
            elif domain in blocked_domains or usage_log.get(domain, 0) > DAILY_LIMIT:
                driver.execute_script("window.stop(); window.location.href='https://www.blocked.com';")
        except:
            pass
        time.sleep(2)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'parent' and request.form['password'] == 'parent':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            return render_template_string(login_page, error="Invalid credentials")
    return render_template_string(login_page)
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Parental Control Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(to right, #f4f4f4, #e0e0e0);
            padding: 20px;
            animation: fadeIn 0.6s ease-in;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-top: 30px;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from {transform: translateY(20px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ccc;
            text-align: left;
        }
        th {
            background: #333;
            color: white;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        input[type=text] {
            padding: 8px;
            width: 300px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            padding: 8px 15px;
            background: #2575fc;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        button:hover {
            background: #1a5edb;
        }
    </style>
</head>
<body>
    <h1>Parental Control Dashboard</h1>

    <div class="section">
        <form method="post" action="/block">
            <label>Paste website link to block:</label>
            <input type="text" name="url" placeholder="https://www.youtube.com" required>
            <button type="submit">Block</button>
        </form>
        <form method="post" action="/focus" style="margin-top:10px;">
            <button type="submit">{{ 'Disable' if focus else 'Enable' }} Focus Mode</button>
        </form>
        <form method="post" action="/clear" style="margin-top:10px;">
            <button type="submit" style="background:#555;">Clear Usage History</button>
        </form>
    </div>

    <div class="section">
        <form method="post" action="/focus_add">
            <label>Add allowed site for Focus Mode:</label>
            <input type="text" name="url" placeholder="https://www.coursera.org" required>
            <button type="submit">Add to Whitelist</button>
        </form>
    </div>

    <div class="section">
        <h2>Focus Mode Whitelist</h2>
        <table>
            <tr><th>Domain</th><th>Action</th></tr>
            {% for domain in whitelist %}
            <tr>
                <td>{{ domain }}</td>
                <td>
                    <form method="post" action="/focus_remove">
                        <input type="hidden" name="domain" value="{{ domain }}">
                        <button type="submit">Remove</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Top 5 Most Used Domains</h2>
        <table>
            <tr><th>Domain</th><th>Time (s)</th></tr>
            {% for domain, time in top %}
            <tr><td>{{ domain }}</td><td>{{ time }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Usage Log (Over 30 mins)</h2>
        <table>
            <tr><th>Domain</th><th>Time (s)</th><th>Status</th></tr>
            {% for domain, time in usage.items() %}
            <tr>
                <td>{{ domain }}</td>
                <td>{{ time }}</td>
                <td>
                    {% if domain in blocked %}
                        Blocked
                    {% elif time > 3600 %}
                        Auto-Blocked (Daily Limit)
                    {% else %}
                        Allowed
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Blocked Websites</h2>
        <table>
            <tr><th>Domain</th><th>Action</th></tr>
            {% for domain in blocked %}
            <tr>
                <td>{{ domain }}</td>
                <td>
                    <form method="post" action="/unblock">
                        <input type="hidden" name="domain" value="{{ domain }}">
                        <button type="submit">Unblock</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""
login_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
            text-align: center;
            animation: slideUp 0.6s ease-out;
        }
        @keyframes slideUp {
            from {transform: translateY(50px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
        input[type=text], input[type=password] {
            width: 80%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background: #2575fc;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        button:hover {
            background: #1a5edb;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Parental Control Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    filtered_usage = {d: t for d, t in usage_log.items() if t > USAGE_THRESHOLD}
    top_domains = sorted(usage_log.items(), key=lambda x: x[1], reverse=True)[:5]
    return render_template_string(dashboard_html,
        usage=filtered_usage,
        blocked=blocked_domains,
        top=top_domains,
        focus=focus_mode,
        whitelist=focus_whitelist)

@app.route('/block', methods=['POST'])
def block():
    if not session.get('logged_in'):
        return redirect('/')
    url = request.form['url'].strip()
    domain = normalize_domain(url)
    if domain:
        blocked_domains.add(domain)
        save_blocklist()
    return redirect('/dashboard')

@app.route('/unblock', methods=['POST'])
def unblock():
    if not session.get('logged_in'):
        return redirect('/')
    domain = request.form['domain'].strip().lower()
    blocked_domains.discard(domain)
    save_blocklist()
    return redirect('/dashboard')

@app.route('/clear', methods=['POST'])
def clear_history():
    if not session.get('logged_in'):
        return redirect('/')
    global usage_log
    usage_log = {}
    save_usage()
    return redirect('/dashboard')

@app.route('/focus', methods=['POST'])
def toggle_focus():
    if not session.get('logged_in'):
        return redirect('/')
    global focus_mode
    focus_mode = not focus_mode
    return redirect('/dashboard')

@app.route('/focus_add', methods=['POST'])
def add_to_whitelist():
    if not session.get('logged_in'):
        return redirect('/')
    url = request.form['url'].strip()
    domain = normalize_domain(url)
    if domain:
        focus_whitelist.add(domain)
        save_whitelist()
    return redirect('/dashboard')

@app.route('/focus_remove', methods=['POST'])
def remove_from_whitelist():
    if not session.get('logged_in'):
        return redirect('/')
    domain = request.form['domain'].strip().lower()
    focus_whitelist.discard(domain)
    save_whitelist()
    return redirect('/dashboard')

if __name__ == "__main__":
    load_blocklist()
    load_usage()
    load_whitelist()
    threading.Thread(target=track_browser, daemon=True).start()
    app.run(debug=True)