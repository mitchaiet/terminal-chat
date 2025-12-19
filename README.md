# Terminal Chat

Chat interface for IBM 3270 terminals using local LLMs via Ollama.

## Components

- **chat/** - Bash-based chat interface for the terminal
- **web/** - Flask web controller for managing oec sessions  
- **oec/** - [Open Emulator Controller](https://github.com/lowobservable/oec) (submodule)
- **asciiterm/** - [ASCIITerm](https://github.com/mitchaiet/ASCIITerm) (submodule)

## Setup

### Prerequisites

- Python 3.x
- Ollama running locally
- IBM 3270 terminal connected via oec

### Clone with submodules

```bash
git clone --recurse-submodules https://github.com/mitchaiet/terminal-chat.git
```

### Install oec

```bash
cd oec
pip install -e .
```

### Run Web Controller

```bash
cd web
pip install -r requirements.txt
python app.py
```

Access at http://localhost:3270

### Chat Interface

The chat interface runs directly on the terminal via oec. Select "chat" mode in the web controller.

Commands:
- `model` - Switch LLM model
- `clear` - Clear screen
- `quit` - Exit

## Models

Supports any Ollama model. Defaults to llama3.2:3b.
