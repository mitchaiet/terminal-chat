# Terminal Chat Changelog

## Working Configurations

### v1.0 - Simple Chat (WORKING)
- Simple bash script with basic echo statements
- No ASCII art banner
- No clear command at startup
- Uses native terminal line editing (backspace/arrows work)
- File: chat/chat.sh

### Known Issues
- ASCII art banner causes oec session disconnects
- `clear` command at startup breaks terminal line editing
- Python version (chat.py) has issues with oec VT100 mode
- `script` PTY wrapper causes session disconnects

### What Works
- Simple echo statements
- `read -r` for input (native line editing)
- curl to Ollama API
- Python for JSON parsing (inline)

### What Breaks
- printf with format strings
- Complex escape sequences
- clear command before first input
- script -q /dev/null wrapper

## Hardware
- Terminal: IBM 3481 (Model 2, 24x80)
- Keyboard: Memorex 122-key (IBM-TYPEWRITER layout)
- Controller: oec in VT100 mode
- Backend: NVIDIA GB10 with Ollama

### v1.1 - Readline Fix (WORKING)
- Changed `read -r` to `read -e` 
- `read -e` enables readline for proper backspace/arrow keys
- This is the key fix!
