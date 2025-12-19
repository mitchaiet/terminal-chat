#!/bin/bash
# Simple chat - no fancy TUI

OLLAMA="http://localhost:11434"
MODEL="llama3.2:3b"
DIR="$(dirname "$(readlink -f "$0")")"

echo "========================================"
echo "  TERMINAL CHAT"
echo "========================================"
echo "Model: $MODEL"
echo "Commands: model, clear, quit"
echo "========================================"
echo ""

while true; do
    echo -n "YOU> "
    read -r INPUT

    [ -z "$INPUT" ] && continue

    case "$INPUT" in
        quit|q) echo "Goodbye."; exit 0 ;;
        clear) clear; echo "=== TERMINAL CHAT ==="; echo "" ;;
        model)
            echo "1) llama3.2:3b  2) mongo-tom"
            echo -n "Choice: "
            read -r p
            case "$p" in
                1) MODEL="llama3.2:3b" ;;
                2) MODEL="hf.co/exptech/mongo-tom:BF16" ;;
            esac
            echo "Model: $MODEL"
            ;;
        *)
            echo "[thinking...]"
            RESP=$(curl -s --max-time 120 "$OLLAMA/api/chat" \
                -H "Content-Type: application/json" \
                -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"system\",\"content\":\"Keep replies brief, 1-2 sentences. No markdown.\"},{\"role\":\"user\",\"content\":\"$INPUT\"}],\"stream\":false}" 2>/dev/null)

            if [ -n "$RESP" ]; then
                echo "$RESP" | python3 -c "
import sys,json,re
try:
    d=json.load(sys.stdin)
    t=d.get('message',{}).get('content','[error]')
    t=re.sub(r'\*+','',t)
    print('AI> '+t[:200])
except: print('AI> [error]')
" 2>/dev/null
            else
                echo "AI> [no response]"
            fi
            echo ""
            ;;
    esac
done
