#!/usr/bin/env python3
import os, subprocess, signal, time, threading
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)
process = None
auto_restart = False
start_time = None
restart_count = 0
current_app = 'bash'

APPS = {
    'bash': '/bin/bash -l',
    'chat': '/home/mitchaiet/terminal-chat/chat/launch.sh'
}

def watchdog():
    global process, restart_count, start_time
    while True:
        time.sleep(2)
        if auto_restart and process and process.poll() is not None:
            restart_count += 1
            time.sleep(1)
            start_oec()

def start_oec():
    global process, start_time, current_app
    app_cmd = APPS.get(current_app, APPS['bash'])
    cmd = f'cd ~/oec && . .venv/bin/activate && sleep 1 && exec python -m oec /dev/ttyACM0 vt100 {app_cmd}'
    process = subprocess.Popen(cmd, shell=True, executable='/bin/bash',
                               stdout=open('/tmp/oec.log','w'), stderr=subprocess.STDOUT,
                               preexec_fn=os.setsid)
    start_time = time.time()

threading.Thread(target=watchdog, daemon=True).start()

HTML = '''<!DOCTYPE html>
<html><head><title>IBM 3270 Control</title>
<style>
body{background:#0a0a1a;color:#00ff41;font-family:'IBM Plex Mono',monospace;margin:0;padding:20px;min-height:100vh}
.container{max-width:800px;margin:0 auto}
h1{text-align:center;font-size:28px;margin-bottom:5px;text-shadow:0 0 10px #00ff41}
.sub{text-align:center;color:#666;margin-bottom:30px}
.panel{background:#111;border:2px solid #00ff41;padding:25px;margin:20px 0;border-radius:8px}
.status-big{font-size:64px;text-align:center;margin:10px 0}
.on{color:#00ff41;text-shadow:0 0 20px #00ff41}
.off{color:#ff4141;text-shadow:0 0 20px #ff4141}
.status-text{text-align:center;font-size:18px;margin:15px 0}
.info{display:flex;justify-content:space-around;margin:20px 0;font-size:14px;color:#888}
.buttons{display:flex;gap:15px;justify-content:center;margin:25px 0}
button{font-size:18px;padding:12px 35px;cursor:pointer;border:2px solid;font-family:inherit;background:#0a0a1a;border-radius:5px;transition:all 0.2s}
.start{color:#00ff41;border-color:#00ff41}
.start:hover:not(:disabled){background:#00ff41;color:#000}
.stop{color:#ff4141;border-color:#ff4141}
.stop:hover:not(:disabled){background:#ff4141;color:#000}
button:disabled{opacity:0.3;cursor:not-allowed}
.app-select{margin:20px 0;text-align:center}
.app-select label{margin:0 15px;cursor:pointer}
.app-select input{margin-right:5px}
.log{background:#050505;padding:15px;font-size:11px;height:120px;overflow-y:auto;border:1px solid #333;border-radius:4px;margin-top:20px}
.log-entry{padding:3px 0;border-bottom:1px solid #222}
.log-time{color:#555}
.toggle{margin:15px 0;text-align:center}
.toggle label{cursor:pointer;color:#888}
.footer{text-align:center;margin-top:30px;color:#444;font-size:12px}
</style></head><body>
<div class="container">
<h1>IBM 3270 TERMINAL</h1>
<div class="sub">IBM 3481 @ /dev/ttyACM0</div>

<div class="panel">
<div class="status-big" id="icon">*</div>
<div class="status-text" id="status">Loading...</div>
<div class="info">
<span id="uptime">Uptime: --</span>
<span id="restarts">Restarts: 0</span>
<span id="app">App: --</span>
</div>
</div>

<div class="panel">
<div class="app-select">
<strong>Terminal Application:</strong><br><br>
<label><input type="radio" name="app" value="bash" checked onchange="setApp(this.value)"> Bash Shell</label>
<label><input type="radio" name="app" value="chat" onchange="setApp(this.value)"> Mainframe Chat (LLM)</label>
</div>
</div>

<div class="buttons">
<button class="start" id="startBtn" onclick="doStart()">START</button>
<button class="stop" id="stopBtn" onclick="doStop()">STOP</button>
</div>

<div class="toggle">
<label><input type="checkbox" id="autoRestart" onchange="toggleAuto()"> Auto-restart on disconnect</label>
</div>

<div class="panel">
<strong>Activity Log</strong>
<div class="log" id="log"></div>
</div>

<div class="footer">IBM 3270 Terminal Controller | oec</div>
</div>

<script>
function log(msg) {
    var el = document.getElementById('log');
    var time = new Date().toLocaleTimeString();
    el.innerHTML = '<div class="log-entry"><span class="log-time">' + time + '</span> ' + msg + '</div>' + el.innerHTML;
}

function updateUI(data) {
    var icon = document.getElementById('icon');
    var status = document.getElementById('status');
    var startBtn = document.getElementById('startBtn');
    var stopBtn = document.getElementById('stopBtn');

    icon.className = 'status-big ' + (data.running ? 'on' : 'off');
    status.textContent = data.running ? 'CONNECTED' : 'DISCONNECTED';
    startBtn.disabled = data.running;
    stopBtn.disabled = !data.running;

    document.getElementById('uptime').textContent = 'Uptime: ' + (data.uptime || '--');
    document.getElementById('restarts').textContent = 'Restarts: ' + data.restarts;
    document.getElementById('app').textContent = 'App: ' + (data.app === 'chat' ? 'Mainframe Chat' : 'Bash');
    document.getElementById('autoRestart').checked = data.auto_restart;

    var radios = document.getElementsByName('app');
    for (var i = 0; i < radios.length; i++) {
        if (radios[i].value === data.app) radios[i].checked = true;
    }
}

async function check() {
    try {
        var r = await fetch('/status');
        updateUI(await r.json());
    } catch(e) {}
}

async function doStart() {
    log('Starting terminal session...');
    var r = await fetch('/start', {method: 'POST'});
    var d = await r.json();
    log(d.success ? 'Session started - check your terminal!' : 'Error: ' + d.error);
    check();
}

async function doStop() {
    log('Stopping terminal session...');
    await fetch('/stop', {method: 'POST'});
    log('Session stopped');
    check();
}

async function setApp(appName) {
    await fetch('/setapp?app=' + appName);
    log('Application set to: ' + (appName === 'chat' ? 'Mainframe Chat' : 'Bash'));
}

async function toggleAuto() {
    var v = document.getElementById('autoRestart').checked;
    await fetch('/auto?v=' + (v?1:0));
    log('Auto-restart ' + (v ? 'enabled' : 'disabled'));
}

log('Controller ready');
check();
setInterval(check, 2000);
</script>
</body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/status')
def status():
    global process, auto_restart, start_time, restart_count, current_app
    running = process is not None and process.poll() is None
    uptime = None
    if running and start_time:
        secs = int(time.time() - start_time)
        mins, secs = divmod(secs, 60)
        hrs, mins = divmod(mins, 60)
        uptime = f"{hrs}h {mins}m {secs}s" if hrs else f"{mins}m {secs}s" if mins else f"{secs}s"
    return jsonify({
        'running': running,
        'auto_restart': auto_restart,
        'uptime': uptime,
        'restarts': restart_count,
        'app': current_app
    })

@app.route('/start', methods=['POST'])
def start_route():
    global process, restart_count
    if process and process.poll() is None:
        return jsonify({'success': False, 'error': 'Already running'})
    restart_count = 0
    start_oec()
    return jsonify({'success': True})

@app.route('/stop', methods=['POST'])
def stop_route():
    global process, auto_restart
    old_auto = auto_restart
    auto_restart = False
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except: pass
        process = None
    auto_restart = old_auto
    return jsonify({'success': True})

@app.route('/auto')
def toggle_auto():
    global auto_restart
    auto_restart = request.args.get('v', '1') == '1'
    return jsonify({'auto_restart': auto_restart})

@app.route('/setapp')
def set_app_route():
    global current_app
    current_app = request.args.get('app', 'bash')
    if current_app not in APPS:
        current_app = 'bash'
    return jsonify({'app': current_app})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3270, threaded=True)
