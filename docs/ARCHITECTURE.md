# Architecture

Cross-platform CPU-based voice transcription using faster-whisper large-v3-turbo (INT8).

## Directory Structure

```
pink-transcriber-cpu/
├── src/pink_transcriber/
│   ├── __init__.py                # Package version
│   ├── config.py                  # Platform detection, socket/TCP config, cache paths
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── client.py              # CLI client - connects to server via socket/TCP
│   │   └── server.py              # Main server - sets up socket server and coordinates workers
│   ├── core/
│   │   ├── __init__.py
│   │   └── model.py               # Model loading (faster-whisper) and transcription logic
│   └── daemon/
│       ├── __init__.py
│       ├── singleton.py           # Single instance enforcement - kills other running instances
│       └── worker.py              # Async queue worker - processes transcription requests
├── pyproject.toml                 # Project metadata, dependencies, entry points
└── README.md                      # Usage instructions
```

## Files

### `src/pink_transcriber/config.py`
Platform detection and configuration management. Determines socket path (Unix) vs TCP host/port (Windows), defines supported audio formats, implements model cache directory logic.

### `src/pink_transcriber/cli/client.py`
CLI client that validates audio files, connects to server via platform-specific socket, sends file path, receives transcription result.

### `src/pink_transcriber/cli/server.py`
Main server entry point. Sets process title, creates async queue, starts transcription worker, sets up socket server, loads model in background, handles graceful shutdown.

### `src/pink_transcriber/core/model.py`
Loads faster-whisper large-v3-turbo model with CPU/INT8 compute type. Provides transcription function with VAD filtering and beam search.

### `src/pink_transcriber/daemon/singleton.py`
Enforces single server instance by scanning for processes with project identifiers, walking up process tree to find root, killing entire tree recursively.

### `src/pink_transcriber/daemon/worker.py`
Async queue worker that processes transcription requests sequentially. Receives requests with audio path and result future, runs blocking transcription in executor.

## Entry Points

```bash
# Start server
uv run pink-transcriber-server

# Transcribe audio
uv run pink-transcriber audio.ogg

# Health check
uv run pink-transcriber --health
```

## Key Concepts

**Client-Server Architecture** — Unix domain socket (`/tmp/pink-transcriber.sock`) on Unix, TCP socket (`127.0.0.1:19876`) on Windows. Client sends file path, server responds with transcribed text using newline-delimited protocol.

**Async Processing** — Server uses asyncio for concurrent connections, single worker queue processes transcriptions sequentially (model not thread-safe), blocking operations run in executor.

**Singleton Enforcement** — Server ensures only one instance runs system-wide by scanning processes, walking up to root process, and killing entire tree to prevent duplicate model loading and socket conflicts.

**Model Caching** — Model downloaded once to cache directory. Priority: `PINK_TRANSCRIBER_MODEL_DIR` env > package `./models/` > user data dir (`~/.local/share/pink-transcriber/models` on Unix, `%LOCALAPPDATA%\pink-transcriber\models` on Windows).

**Error Handling** — Client validates file existence and format before sending. Server returns `ERROR:` prefix for failures. Graceful shutdown with signal handlers, health check command for monitoring.
