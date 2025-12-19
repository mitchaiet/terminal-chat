#!/usr/bin/env python3
"""IBM 3270 Terminal Chat - Simple version"""
import sys
import os
import json
import requests
import re
import time
import readline  # Enable line editing
def clean_input(s):
    """Process backspace chars"""
    result = []
    for c in s:
        if c == chr(8) or c == chr(127):  # BS or DEL
            if result: result.pop()
        else:
            result.append(c)
    return "".join(result)


OLLAMA = "http://localhost:11434"
MODEL = "llama3.2:3b"
SYSTEM = "You are a helpful assistant. Keep replies to 1-2 sentences. No markdown or special formatting."

def clear():
    os.system('clear')

def banner():
    global MODEL
    clear()
    print("+" + "-"*78 + "+")
    print("|" + " "*78 + "|")
    print("|   _______ ______ _____  __  __ _____ _   _          _" + " "*22 + "|")
    print("|  |__   __|  ____|  __ \\|  \\/  |_   _| \\ | |   /\\   | |" + " "*17 + "|")
    print("|     | |  | |__  | |__) | \\  / | | | |  \\| |  /  \\  | |" + " "*17 + "|")
    print("|     | |  |  __| |  _  /| |\\/| | | | | . ` | / /\\ \\ | |" + " "*17 + "|")
    print("|     | |  | |____| | \\ \\| |  | |_| |_| |\\  |/ ____ \\| |____" + " "*12 + "|")
    print("|     |_|  |______|_|  \\_\\_|  |_|_____|_| \\_/_/    \\_\\______|" + " "*10 + "|")
    print("|" + " "*78 + "|")
    print("|" + "C H A T   I N T E R F A C E".center(78) + "|")
    print("|" + " "*78 + "|")
    print("+" + "-"*78 + "+")
    model_display = MODEL[:68]
    print(f"| MODEL: {model_display:<69}|")
    print("| CMDS: model | clear | quit" + " "*49 + "|")
    print("+" + "-"*78 + "+")
    sys.stdout.flush()

def chat(msg):
    global MODEL
    print("  [PROCESSING...]", flush=True)
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": msg}
            ],
            "stream": False
        }, timeout=120)
        data = r.json()
        text = data.get("message", {}).get("content", "[No response]")
        # Strip markdown
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Word wrap
        words = text.split()
        lines = []
        line = ""
        for w in words:
            if len(line) + len(w) + 1 > 72:
                lines.append(line)
                line = w
            else:
                line = line + " " + w if line else w
        if line:
            lines.append(line)
        print()
        for l in lines:
            print(f"  AI> {l}")
        print()
    except Exception as e:
        print(f"  AI> [ERROR: {e}]")
    sys.stdout.flush()

def main():
    global MODEL
    clear()
    print("  Connecting to Ollama...", flush=True)
    try:
        requests.get(f"{OLLAMA}/api/tags", timeout=5)
        print("  [OK] Connected")
    except:
        print("  [ERROR] Cannot connect")
        input("  Press ENTER...")
        return

    time.sleep(1)
    banner()

    while True:
        try:
            print(flush=True)
            inp = clean_input(input("  YOU> "))
            if not inp:
                continue
            cmd = inp.lower().strip()
            if cmd in ("quit", "exit", "q"):
                clear()
                print("  Goodbye.")
                break
            elif cmd == "clear":
                banner()
            elif cmd == "model":
                print("  1) llama3.2:3b  2) mongo-tom  3) qwen2.5-coder:32b")
                print("  4) llama3.1:70b 5) qwen2.5:72b 6) deepseek-r1:70b")
                p = input("  Choice: ")
                models = {
                    "1": "llama3.2:3b",
                    "2": "hf.co/exptech/mongo-tom:BF16",
                    "3": "qwen2.5-coder:32b",
                    "4": "llama3.1:70b",
                    "5": "qwen2.5:72b",
                    "6": "deepseek-r1:70b"
                }
                if p in models:
                    MODEL = models[p]
                    print(f"  [OK] {MODEL}")
                    time.sleep(1)
                    banner()
            elif cmd in ("help", "?"):
                print("  model - Change AI model")
                print("  clear - Clear screen")
                print("  quit  - Exit")
            else:
                chat(inp)
        except (KeyboardInterrupt, EOFError):
            print()
            break

if __name__ == "__main__":
    main()
