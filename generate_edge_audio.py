#!/usr/bin/env python3
"""Create Hindi neural narration via the Edge TTS community package."""
import argparse, asyncio, re
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent
def split_text(text, limit=4000):
    paras=[p.strip() for p in re.split(r"\n\s*\n",text) if p.strip()]
    chunks=[]; current=""
    for p in paras:
        while len(p)>limit:
            cut=max(p.rfind("।",0,limit),p.rfind(".",0,limit),p.rfind(" ",0,limit))
            if cut<limit//2: cut=limit
            chunks.append(p[:cut+1].strip()); p=p[cut+1:].strip()
        candidate=(current+"\n\n"+p).strip()
        if current and len(candidate)>limit: chunks.append(current); current=p
        else: current=candidate
    if current: chunks.append(current)
    return chunks
async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="scripts/panchayat-season-5-hinglish.txt")
    ap.add_argument("--output",default="audio/Panchayat_Season_5_Hinglish_Narration.mp3")
    ap.add_argument("--voice",default="hi-IN-MadhurNeural")
    ap.add_argument("--rate",default="-3%")
    ap.add_argument("--pitch",default="+0Hz")
    a=ap.parse_args()
    src=Path(a.input); src=src if src.is_absolute() else ROOT/src
    if not src.exists(): raise SystemExit(f"Script not found: {src}")
    text=src.read_text(encoding="utf-8").strip()
    # Do not speak stage directions such as [INTRO] or [SECTION 1].
    text="\n".join(line for line in text.splitlines() if not (line.strip().startswith("[") and line.strip().endswith("]"))).strip()
    if not text: raise SystemExit("Script is empty.")
    out=Path(a.output); out=out if out.is_absolute() else ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True); tmp=out.parent/".tts_parts"; tmp.mkdir(exist_ok=True)
    parts=[]
    for i,chunk in enumerate(split_text(text),1):
        target=tmp/f"part_{i:03d}.mp3"; print(f"Generating part {i}")
        await asyncio.wait_for(edge_tts.Communicate(chunk,a.voice,rate=a.rate,pitch=a.pitch).save(str(target)), timeout=180); parts.append(target)
    def mp3_frames(path):
        data=path.read_bytes()
        # Remove per-part ID3 tags before joining MPEG audio frames.
        if data.startswith(b"ID3") and len(data)>=10:
            size=((data[6]&0x7f)<<21)|((data[7]&0x7f)<<14)|((data[8]&0x7f)<<7)|(data[9]&0x7f)
            data=data[10+size:]
        if len(data)>=128 and data[-128:-125]==b"TAG":
            data=data[:-128]
        return data
    out.write_bytes(b"".join(mp3_frames(p) for p in parts))
    print(f"Audio saved: {out} ({out.stat().st_size} bytes)")
if __name__=="__main__": asyncio.run(main())
