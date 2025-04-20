from groq import Groq
from utils.audio import to_wav, chunk_words
from config import MODEL_ID, CHAT_MODEL, TAG_SYS_PROMPT, CHUNK_TOKENS

client = Groq()

def transcribe(wav_path):
    with open(wav_path, "rb") as f:
        return client.audio.transcriptions.create(
            file=f,
            model=MODEL_ID,
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )

def tag_speakers(words):
    """Chunk word list → ask Groq chat to attach speaker labels."""
    def tokens(lst): return sum(len(w["text"].split()) for w in lst)
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if tokens(cur) > CHUNK_TOKENS:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)

    tagged = []
    for ch in chunks:
        raw = " ".join(w["text"] for w in ch)
        msg = [
            {"role": "system", "content": TAG_SYS_PROMPT},
            {"role": "user", "content": raw}
        ]
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=msg,
            temperature=0.0
        )
        tagged.extend(parse_chat(resp.choices[0].message.content, ch))
    return tagged

def parse_chat(text, orig_words):
    """
    Very simple parser: each returned line has the form
        'Name (Role): sentence …'
    We map back to orig word timestamps by sentence order.
    """
    out, idx = [], 0
    for line in text.splitlines():
        if ":" not in line:
            continue
        head, body = line.split(":", 1)
        spk = head.strip()
        words = body.strip().split()
        # glue timing from orig_words slice
        slice_len = len(words)
        seg = orig_words[idx: idx+slice_len]
        if not seg: continue
        out.append({
            "speaker": spk,
            "start": seg[0]["start"],
            "end":   seg[-1]["end"],
            "text":  body.strip()
        })
        idx += slice_len
    return out
