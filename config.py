# config.py  – central constants for the fcgov‑rag project
from pathlib import Path

# Folders --------------------------------------------------------------------
BASE_DIR   = Path(__file__).parent.resolve()
VIDEO_DIR  = BASE_DIR / "videos"      # raw .mp4 files
AUDIO_DIR  = BASE_DIR / "audio"       # extracted .wav files
OUTPUT_DIR = BASE_DIR / "markdown"    # final .md transcripts

for p in (VIDEO_DIR, AUDIO_DIR, OUTPUT_DIR):
    p.mkdir(exist_ok=True, parents=True)

# Groq / model settings ------------------------------------------------------
# Supply your key in the shell:  export GROQ_API_KEY="sk‑…"
MODEL_ID    = "distil-whisper-large-v3"  # transcription
CHAT_MODEL  = "llama3-70b-8192"          # speaker‑tagging
MONTHS_BACK = 6                          # default scrape window
TAG_SYS_PROMPT = (
    "You are a meeting‑minutes assistant for Fort Collins City Council. "
    "Return 'Speaker Name (Role): text' lines for each utterance."
)
CHUNK_TOKENS = 3500                      # split long transcripts for chat
