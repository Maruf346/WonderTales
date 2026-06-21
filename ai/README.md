# WonderTels Hub – AI Layer

Production-ready FastAPI service powering:
- **Story generation** via OpenAI GPT-4o
- **Voice narration** via ElevenLabs TTS
- **Voice cloning** via ElevenLabs Instant Voice Cloning (Premium)

---

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Run the server

```bash
python main.py
```

To move the server off a busy port, change `APP_PORT` in `.env` and rerun.
Set `LAN_HOST`, `TAILSCALE_HOST`, and `TAILSCALE_PATH` if you want the startup banner to print shareable LAN and Tailscale URLs.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/stories/generate` | Generate new story + narration |
| `POST` | `/stories/continue` | Continue existing story |
| `GET` | `/voices` | List preset voices |
| `POST` | `/voices/clone` | Clone family voice *(Premium)* |
| `GET` | `/health` | Health check |

---

## Example Requests

### Generate a Story

```bash
curl -X POST http://localhost:8000/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "child_profile": {
      "name": "Amara",
      "age": 6,
      "interests": ["dinosaurs", "space"]
    },
    "language": "en",
    "narrator_voice": "primary_female",
    "theme": "bedtime"
  }'
```

**Response:**
```json
{
  "story_id": "40d71ba886ba4a95bba2d422bb06a446",
  "story_text": "Once upon a time, in a land where dinosaurs roamed the stars...",
  "audio_url": "http://localhost:8000/audio/abc123def456.mp3",
  "language": "en",
  "voice_used": "primary_female"
}
```

**Voice Tiers Available:**
- `primary_female`, `primary_male` – Main soothing narration (recommended for story opening)
- `secondary_female`, `secondary_male` – Softer alternatives
- `child_female`, `child_male` – Character dialogue only

### Continue a Story (Token-Optimized)

Use the `story_id` returned from generation to avoid resending the full story text:

```bash
curl -X POST http://localhost:8000/stories/continue \
  -H "Content-Type: application/json" \
  -d '{
    "child_profile": {"name": "Amara", "age": 6, "interests": ["dinosaurs"]},
    "story_id": "40d71ba886ba4a95bba2d422bb06a446",
    "language": "en",
    "narrator_voice": "primary_female"
  }'
```

> **Tip:** Passing `story_id` (preferred) saves ~60–80% of API tokens vs. resending `previous_story_text`.

### Clone a Voice

```bash
curl -X POST http://localhost:8000/voices/clone \
  -F "voice_name=Mum's Bedtime Voice" \
  -F "description=Warm family narrator" \
  -F "audio_file=@/path/to/recording.mp3"
```

**Response:**
```json
{
  "voice_id": "abc123xyz",
  "voice_name": "Mum's Bedtime Voice",
  "message": "Voice cloned successfully. Use voice_id in story requests."
}
```

Then use in story generation:
```json
{
  "child_profile": {"name": "Amara", "age": 6},
  "cloned_voice_id": "abc123xyz",
  ...
}
```

---

## Voice Cloning – How It Works

ElevenLabs Instant Voice Cloning is **fully supported** via their API:

1. Upload 1–5 minutes of clean speech audio (MP3/WAV/M4A)
2. ElevenLabs returns a `voice_id` 
3. Store the `voice_id` in your database linked to the user
4. Pass `cloned_voice_id` in any story/continue request

**Requirements:**
- ElevenLabs **Creator plan or higher** for voice cloning
- Audio: clean speech, minimal background noise, mono or stereo
- Format: MP3, WAV, M4A, WebM — max 30 MB

---

## Docker Deployment

```bash
docker build -t wondertels-ai .
docker run -p 8000:8000 --env-file .env wondertels-ai
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI secret key |
| `OPENAI_MODEL` | Model to use (default: `gpt-4o`) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_PRIMARY_FEMALE` | Primary soothing female narrator (main) |
| `ELEVENLABS_VOICE_PRIMARY_MALE` | Primary soothing male narrator (main) |
| `ELEVENLABS_VOICE_SECONDARY_FEMALE` | Secondary softer female narrator (alternative) |
| `ELEVENLABS_VOICE_SECONDARY_MALE` | Secondary softer male narrator (alternative) |
| `ELEVENLABS_VOICE_CHILD_FEMALE` | Child female voice (dialogue only) |
| `ELEVENLABS_VOICE_CHILD_MALE` | Child male voice (dialogue only) |
| `AUDIO_STORAGE_DIR` | Directory to save MP3 files |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |
| `APP_HOST` | Host interface used by the local server |
| `APP_PORT` | Port used by the local server |
| `LAN_HOST` | LAN IP or hostname to show in the startup banner |
| `TAILSCALE_HOST` | Tailscale IP or hostname to show in the startup banner |
| `TAILSCALE_PATH` | Optional path prefix for the Tailscale URL |

---

## Architecture

```
Frontend
   │
   ▼
FastAPI (this service)
   ├── POST /stories/generate
   │      ├── OpenAI GPT-4o  ──→  story text
   │      └── ElevenLabs TTS ──→  audio MP3
   │
   ├── POST /stories/continue
   │      ├── OpenAI GPT-4o (with previous context)
   │      └── ElevenLabs TTS
   │
   ├── GET /voices              ──→  preset voice list
   │
   └── POST /voices/clone
          └── ElevenLabs Voice Cloning API ──→  voice_id
```
