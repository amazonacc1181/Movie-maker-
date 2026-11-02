#!/usr/bin/env python3
"""Create Hindi neural narration via the Edge TTS community package."""
import argparse, asyncio, re, subprocess
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent
def split_text(text, limit=2500):
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
        await edge_tts.Communicate(chunk,a.voice,rate=a.rate,pitch=a.pitch).save(str(target)); parts.append(target)
    if len(parts)==1: parts[0].replace(out)
    else:
        concat=tmp/"concat.txt"; concat.write_text("".join("file '"+p.as_posix()+"'\n" for p in parts),encoding="utf-8")
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(out)],check=True)
    print(f"Audio saved: {out} ({out.stat().st_size} bytes)")
if __name__=="__main__": asyncio.run(main())
