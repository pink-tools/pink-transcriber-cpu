# Pink Transcriber CPU

Voice-to-text that works anywhere. No GPU needed.

Cross-platform fallback when you don't have CUDA or Apple Silicon.

## Quick Start

```bash
git clone https://github.com/pink-tools/pink-transcriber-cpu
cd pink-transcriber-cpu
uv sync
uv run pink-transcriber-server
```

First run downloads the model (~1.5GB).

## Requirements

- macOS, Windows, or Linux
- Python 3.10–3.12
- [uv](https://docs.astral.sh/uv/)

## Usage

**Start server:**
```bash
uv run pink-transcriber-server
```

**Transcribe:**
```bash
uv run pink-transcriber audio.ogg
```

**Check health:**
```bash
uv run pink-transcriber --health
```

Supports: wav, ogg, mp3, m4a, flac, opus, aiff

## Customization

Adjust format, speed, output and more:
```bash
uv run pink-transcriber --help
```

## License

MIT
