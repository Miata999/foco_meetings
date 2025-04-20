import datetime as dt
import json
import re
from pathlib import Path
from typing import Optional
import bs4             # Beautiful Soup 4
import requests

from config import MONTHS_BACK, VIDEO_DIR

ARCHIVE = "https://www.fcgov.com/fctv/video-archive"
DATE_RX = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2})\b")   # matches 4/17/25, 12/3/24 …
def iter_meetings():
    cutoff = dt.date.today() - dt.timedelta(days=30 * MONTHS_BACK)
    soup   = bs4.BeautifulSoup(requests.get(ARCHIVE).text, "html.parser")

    for row in soup.select("tr"):
        tds = [td.get_text(strip=True) for td in row("td")]
        if len(tds) < 1:
            continue

        # --- 1.  pull date from any cell that has it -----------------------
        raw_date = None
        for cell in tds:
            m = DATE_RX.search(cell)
            if m:
                raw_date = m.group(1)
                break
        if not raw_date:
            continue                     # skip rows without a date at all

        try:
            date_obj = dt.datetime.strptime(raw_date, "%m/%d/%y").date()
        except ValueError:
            continue                     # malformed date string → skip

        if date_obj < cutoff:
            continue

        # --- 2.  build title ----------------------------------------------
        # If the first cell already contained date text, strip it off.
        title = DATE_RX.sub("", tds[0]).strip()
        if not title:
            title = "City Council Meeting"

        # --- 3.  grab the show‑page link -----------------------------------
        link_tag = row.select_one("a[href*=show]")
        if not link_tag:
            continue
        href = link_tag["href"]
        show_url = href if href.startswith("http") else f"https:{href}"

        yield {
            "title": title,
            "date":  str(date_obj),
            "show":  show_url,
        }

def show_to_mp4(show_url: str) -> Optional[str]:
    """
    Return the first .mp4 link found on the Cablecast show page,
    or None if no such link exists.
    """
    html = requests.get(show_url, timeout=20).text
    matches = re.findall(r"https?://[^\"']+?\.mp4", html)
    return matches[0] if matches else None


def save_manifest() -> None:
    """
    Build videos/manifest.json with only those meetings that have
    a valid MP4 link.  Skips rows that are missing VOD files.
    """
    VIDEO_DIR.mkdir(exist_ok=True, parents=True)
    out = []

    for meta in iter_meetings():
        mp4_url = show_to_mp4(meta["show"])
        if not mp4_url:
            # log & continue if the show page has no downloadable asset
            print(f"⚠️  No MP4 found → skipping {meta['show']}")
            continue

        meta["mp4"] = mp4_url
        out.append(meta)

    # write final list to disk
    manifest_path = VIDEO_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(out, indent=2))
    print(f"✅  Saved manifest with {len(out)} videos → {manifest_path}")


if __name__ == "__main__":
    save_manifest()
