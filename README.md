# Parent-control-Dashboard
A modular, real-time parental control system designed for digital discipline and behavioral governance. Built with Flask and Selenium, this tool tracks browser usage, enforces domain restrictions, and visualizes user behavior—all through a sleek, interactive dashboard.
🔐 Secure Access
Animated login screen with session protection

Blocks dashboard access unless authenticated

Default credentials: Username: parent, Password: parent

🖥️ Real-Time Monitoring
Browser tracking via Selenium

Domain normalization using urllib.parse

Time logging per domain

Persistent logs saved in usage_log.json

🚫 Domain Blocking
Manual blocking: paste any site to block instantly

Auto-blocking: domains exceeding 1 hour/day are blocked

Redirect logic: blocked domains redirect to https://www.blocked.com

Unblock controls via dashboard

⏱️ Focus Mode
Toggle button to enable/disable Focus Mode

Whitelist logic: only allowed domains accessible during Focus Mode

Custom whitelist management via dashboard

Optional timer (e.g., 45 minutes) for timed focus sessions

📊 Usage Analytics
Top 5 domains visualization

Filtered log: domains with usage over 30 minutes

Clear history button (preserves blocklist)

CSV export for usage data

🌙 UI Enhancements
Dark mode toggle

Toast notifications for actions (e.g., “Blocked!”, “Unblocked!”)

Animated sections: fade-ins, slide-ups, hover effects

🧑‍💼 Multi-User Profiles (Optional)
Profile switching for multiple users

Per-profile logs: separate blocklist, whitelist, and usage files

🧰 Technologies & Libraries Used
Backend (Python + Flask):

Flask: routing and session management

Selenium: browser automation

threading: background tracking

json: persistent data storage

urllib.parse: domain extraction

session: secure login state

Frontend (HTML + CSS + JS):

HTML forms for login, blocking, whitelist management

CSS for custom styling and animations

JavaScript functions:

showToast() – feedback messages

toggleDarkMode() – theme switching

Files & Data Structures:

app.py or traffic_controller.py: main Flask app

usage_log.json: time spent per domain

blocked_domains.json: manually blocked domains

focus_whitelist.json: allowed domains during Focus Mode

requirements.txt: dependency list

🧭 Demo Highlights
Login → dashboard loads with animation

Paste https://www.instagram.com → gets blocked

Visit site → auto-redirects to block page

Enable Focus Mode → only educational sites allowed

Add coursera.org to whitelist → now accessible during Focus

View top domains → see time distribution

Export logs → download CSV

Switch profile → new user, new rules
