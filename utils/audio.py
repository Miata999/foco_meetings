import ffmpeg, pathlib
from config import AUDIO_DIR
AUDIO_DIR.mkdir(exist_ok=True, parents=True)

def to_wav(mp4: pathlib.Path) -> pathlib.Path:
    wav = AUDIO_DIR / (mp4.stem + ".wav")
    if wav.exists(): return wav
    ffmpeg.input(str(mp4)).output(str(wav), ac=1, ar="16k", loglevel="quiet").run()
    return wav
def chunk_words(words, max_tokens):
    cur, chunks, tok = [], [], 0
    for w in words:
        t = len(w["text"].split())
        if tok + t > max_tokens:
            chunks.append(cur); cur=[]; tok=0
        cur.append(w); tok += t
    if cur: chunks.append(cur)
    return chunks
