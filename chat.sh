#!/bin/bash
# IBM 3270 Mainframe Chat v4 - Short responses, no markdown

OLLAMA="http://localhost:11434"
MODEL="llama3.2:3b"
SYSTEM="You are a helpful assistant. Keep replies to 1-2 sentences. No markdown or special formatting."
PARSE="$HOME/mainframe-chat/parse.py"

clear
echo "========================================"
echo "     IBM 3270 MAINFRAME CHAT"
echo "========================================"
echo ""
echo "Connecting..."

if ! curl -s --max-time 5 "$OLLAMA/api/tags" > /dev/null 2>&1; then
    echo "ERROR: Cannot reach Ollama"
    read -r
    exit 1
fi

echo "Ready! Model: $MODEL"
echo ""
echo "Commands: model, clear, quit"
echo "========================================"

send_message() {
    local msg="$1"

    echo ""
    echo -n "AI: "

    # Use chat API with system prompt
    local raw=$(curl -s --max-time 120 "$OLLAMA/api/chat" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"system\",\"content\":\"$SYSTEM\"},{\"role\":\"user\",\"content\":\"$msg\"}],\"stream\":false}" 2>/dev/null)

    if [ -z "$raw" ]; then
        echo "[No response]"
        return
    fi

    # Parse with external Python script
    local answer=$(echo "$raw" | python3 "$PARSE" 2>/dev/null)

    if [ -z "$answer" ]; then
        echo "[Empty response]"
    else
        echo "$answer" | fold -s -w 76
    fi
    echo ""
}

# Main loop
while true; do
    echo "----------------------------------------"
    echo -n "YOU: "
    read -r INPUT

    [ -z "$INPUT" ] && continue

    case "$INPUT" in
        quit|exit|q)
            echo "Goodbye!"
            exit 0
            ;;
        clear)
            clear
            echo "=== MAINFRAME CHAT ==="
            echo "Model: $MODEL"
            ;;
        model)
            echo ""
            echo "1) llama3.2 (3B) - fast"
            echo "2) mongo-tom (8B)"
            echo "3) qwen2.5-coder (32B)"
            echo "4) llama3.1 (70B)"
            echo "5) qwen2.5 (72B)"
            echo "6) deepseek-r1 (70B)"
            echo -n "Choice: "
            read -r pick
            case "$pick" in
                1) MODEL="llama3.2:3b" ;;
                2) MODEL="hf.co/exptech/mongo-tom:BF16" ;;
                3) MODEL="qwen2.5-coder:32b" ;;
                4) MODEL="llama3.1:70b" ;;
                5) MODEL="qwen2.5:72b" ;;
                6) MODEL="deepseek-r1:70b" ;;
            esac
            echo "Now using: $MODEL"
            ;;
        *)
            send_message "$INPUT"
            ;;
    esac
done
