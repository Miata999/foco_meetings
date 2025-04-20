import requests, os, tqdm, pathlib, json
from config import VIDEO_DIR

def download(url, dest):
    tmp = dest.with_suffix(".part")
    headers = {}
    if tmp.exists():
        headers["Range"] = f"bytes={tmp.stat().st_size}-"
    with requests.get(url, stream=True, headers=headers) as r, \
         open(tmp, "ab") as f, tqdm.tqdm(total=int(r.headers.get("content-length",0)),
                                         unit="B", unit_scale=True) as bar:
        for chunk in r.iter_content(chunk_size=524288):
            f.write(chunk); bar.update(len(chunk))
    tmp.rename(dest)

def run():
    manifest = json.loads((VIDEO_DIR/"manifest.json").read_text())
    for m in manifest:
        fn = VIDEO_DIR / f'{m["date"]}_{m["title"].replace(" ","_")}.mp4'
        if not fn.exists():
            download(m["mp4"], fn)

if __name__ == "__main__":
    run()
