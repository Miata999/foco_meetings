import json, textwrap, itertools, pathlib
from config import OUTPUT_DIR, VIDEO_DIR

def md_from_words(title, date, url, words):
    def hhmmss(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h:02d}:{m:02d}:{s:05.2f}"
    lines=[]
    for spk, chunk in itertools.groupby(words, key=lambda w: w.get("speaker","SPEAKER")):
        chunk=list(chunk)
        stamp=hhmmss(chunk[0]["start"])
        text=" ".join(w["text"] for w in chunk)
        lines.append(f"### {stamp}\n**{spk}**: {text}\n")
    header=f"---\ntitle: \"{title}\"\ndate: {date}\nvideo_url: {url}\n---\n"
    return header + "\n".join(lines)

def run(manifest_json):
    meta=json.loads(manifest_json.read_text())
    for m in meta:
        md=md_from_words(m["title"],m["date"],m["mp4"],m["words"])
        out=OUTPUT_DIR / (m['date']+"_"+m['title'].replace(" ","_")+".md")
        out.write_text(md)

if __name__=="__main__":
    run(VIDEO_DIR/"manifest.json")
