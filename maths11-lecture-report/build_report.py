#!/usr/bin/env python3
"""Fetch selected Class 11 Maths YouTube metadata with yt-dlp and create PDF/CSV/JSON."""
from __future__ import annotations
import csv, json, os, sys, time, traceback
from datetime import datetime
from pathlib import Path
from yt_dlp import YoutubeDL
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, LongTable,
    PageBreak, KeepTogether
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

# Teacher priority applied from the uploaded PDF: Sachin > Tarun > Ashish.
LECTURES = [
    (1, "Basic Maths", "Sachin Sir", "6I-EMg_z3XY"),
    (2, "Sets", "Sachin Sir", "4Ueyba595R0"),
    (3, "Trigonometric Functions", "Tarun Sir", "0DgG7LxiYzk"),
    (4, "Trigonometric Equation", "Sachin Sir", "o7reW9nkHoU"),
    (5, "Quadratic Equation", "Sachin Sir", "5NWibE8esMs"),
    (6, "Sequence & Series", "Sachin Sir", "M5g9bPWpzag"),
    (7, "Relations and Functions", "Sachin Sir", "Qs0wRt70mC4"),
    (8, "Permutation & Combination", "Tarun Sir", "Cq9SqJPC0Dk"),
    (9, "Binomial Theorem", "Sachin Sir", "YiY0Z5sQ47U"),
    (10, "Straight Lines", "Sachin Sir", "gZ735nqr9FI"),
    (11, "Circles", "Tarun Sir", "6JA8YchdQaQ"),
    (12, "Conic Sections: Parabola", "Sachin Sir", "hIeh8YyqgO0"),
    (13, "Conic Sections: Ellipse", "Tarun Sir", "kM1c94BsYwQ"),
    (14, "Conic Sections: Hyperbola", "Ashish Sir", "_z4rBS7pmzQ"),
    (15, "Complex Numbers", "Sachin Sir", "XGFPDkR4-dg"),
    (16, "Limits and Derivatives", "Sachin Sir", "42TAAbPnPF8"),
    (17, "Statistics", "Tarun Sir", "M0wE7kH_ojk"),
    (18, "Probability", "Tarun Sir", "aIaFDoeZE3w"),
    (19, "Introduction to Three Dimensional Geometry", "Ashish Sir", "HH_E3L2cZv0"),
    (20, "Solution of Triangle", "Tarun Sir", "VkUU-jE0kNM"),
]

def date_text(value):
    if not value:
        return None
    s = str(value)
    if len(s) == 8 and s.isdigit():
        try:
            return datetime.strptime(s, "%Y%m%d").strftime("%d %b %Y")
        except ValueError:
            pass
    return s

def fetch_one(item):
    number, chapter, teacher, video_id = item
    url = f"https://www.youtube.com/watch?v={video_id}"
    row = {
        "number": number, "chapter": chapter, "teacher": teacher,
        "video_id": video_id, "url": url, "title": None,
        "duration_seconds": None, "duration": "Unavailable",
        "upload_date_raw": None, "upload_date": "Unavailable",
        "channel": None, "view_count": None, "live_status": None,
        "availability": None, "status": "Pending", "error": None,
        "metadata_extractor": "yt-dlp"
    }
    opts = {
        "quiet": True, "no_warnings": True, "skip_download": True,
        "noplaylist": True, "socket_timeout": 35,
        "retries": 3, "extractor_retries": 3, "fragment_retries": 2,
        "ignoreerrors": False,
        "extractor_args": {"youtube": {"player_client": ["tv", "web_safari"]}},
    }
    last_error = None
    for attempt in range(1, 3):
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info:
                raise RuntimeError("yt-dlp returned no metadata")
            dur = info.get("duration")
            upload = info.get("upload_date") or info.get("release_date")
            if not upload and info.get("timestamp"):
                upload = datetime.fromtimestamp(info["timestamp"]).strftime("%Y%m%d")
            row.update({
                "title": info.get("title"),
                "duration_seconds": int(dur) if dur is not None else None,
                "duration": ydl_utils_duration(dur),
                "upload_date_raw": upload,
                "upload_date": date_text(upload) or "Unavailable",
                "channel": info.get("channel") or info.get("uploader"),
                "view_count": info.get("view_count"),
                "live_status": info.get("live_status") or ("was_live" if info.get("was_live") else "recorded/unknown"),
                "availability": info.get("availability"),
                "status": "Retrieved",
                "error": None,
            })
            return row
        except Exception as exc:
            last_error = str(exc)
            if attempt < 2:
                time.sleep(2)
    row["status"] = "Unavailable"
    row["error"] = (last_error or "Unknown extraction error")[:600]
    return row

def ydl_utils_duration(value):
    if value is None:
        return "Unavailable"
    seconds = max(0, int(value))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"

def safe(value):
    return "" if value is None else str(value)

def build_pdf(rows, path):
    page = landscape(A4)
    doc = SimpleDocTemplate(
        str(path), pagesize=page, rightMargin=10*mm, leftMargin=10*mm,
        topMargin=12*mm, bottomMargin=14*mm, title="Class 11 Maths - Lecture Metadata Report",
        author="Class 11 Maths Lecture Metadata Finder"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=20, leading=24, textColor=colors.HexColor("#172554"),
                              alignment=TA_LEFT, spaceAfter=5))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=8.5, leading=12,
                              textColor=colors.HexColor("#475569")))
    styles.add(ParagraphStyle(name="Cell", parent=styles["Normal"], fontSize=6.5, leading=8,
                              wordWrap="CJK"))
    styles.add(ParagraphStyle(name="CellBold", parent=styles["Cell"], fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=7, leading=9,
                              textColor=colors.HexColor("#475569")))
    ok = [r for r in rows if r["status"] == "Retrieved"]
    measured = [r for r in rows if r["duration_seconds"] is not None]
    total = sum(r["duration_seconds"] or 0 for r in measured)
    total_txt = ydl_utils_duration(total)
    average_txt = ydl_utils_duration(round(total / len(measured))) if measured else "Unavailable"

    story = [
        Paragraph("CLASS 11 MATHEMATICS", styles["ReportTitle"]),
        Paragraph("Lecture metadata report | 20 selected chapters | Metadata extracted using yt-dlp", styles["Sub"]),
        Spacer(1, 5*mm),
    ]
    summary_data = [
        [Paragraph("<b>Lectures retrieved</b>", styles["Small"]),
         Paragraph("<b>Duration available</b>", styles["Small"]),
         Paragraph("<b>Total duration</b>", styles["Small"]),
         Paragraph("<b>Average duration</b>", styles["Small"]),
         Paragraph("<b>Unavailable</b>", styles["Small"])],
        [f"{len(ok)} / 20", f"{len(measured)} / 20", total_txt, average_txt, str(20-len(ok))]
    ]
    summary = Table(summary_data, colWidths=[45*mm, 43*mm, 42*mm, 43*mm, 35*mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9edfa")),
        ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#172554")),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#d7deec")),
        ("INNERGRID",(0,0),(-1,-1),0.35,colors.HexColor("#d7deec")),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,1),(-1,1),12),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    story += [summary, Spacer(1, 5*mm),
              Paragraph("<b>Teacher selection rule:</b> Sachin Sir first; otherwise Tarun Sir; otherwise Ashish Sir, following the uploaded chapter planner. Upload dates are presented as returned by yt-dlp (YYYYMMDD converted to DD Mon YYYY).", styles["Small"]),
              Spacer(1, 4*mm)]

    headers = ["#", "Chapter", "Teacher", "Video title (clickable)", "Duration", "Upload date", "Channel", "Views", "Status / extraction note"]
    data = [[Paragraph(f"<b>{h}</b>", styles["Cell"]) for h in headers]]
    for r in rows:
        title = r["title"] or "Title unavailable"
        link = f'<link href="{r["url"]}" color="#4338ca">{xml_escape(title)}</link>'
        detail = r["status"]
        if r["error"]:
            detail += ": " + r["error"][:180]
        data.append([
            str(r["number"]),
            Paragraph(xml_escape(r["chapter"]), styles["CellBold"]),
            Paragraph(xml_escape(r["teacher"]), styles["Cell"]),
            Paragraph(link, styles["Cell"]),
            r["duration"],
            r["upload_date"],
            Paragraph(xml_escape(r["channel"] or "Unavailable"), styles["Cell"]),
            f'{r["view_count"]:,}' if isinstance(r["view_count"], int) else "Unavailable",
            Paragraph(xml_escape(detail), styles["Cell"]),
        ])
    widths = [8*mm, 39*mm, 19*mm, 57*mm, 19*mm, 23*mm, 35*mm, 16*mm, 48*mm]
    table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172554")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8fc")]),
        ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#dce2ec")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story += [table, Spacer(1, 5*mm),
              Paragraph("Notes: 'Unavailable' means yt-dlp could not obtain that field or the video could not be accessed during this run. Live broadcasts may expose no final duration until processing is complete. The report does not estimate missing values.", styles["Small"]),
              Paragraph(f"Report generated (UTC): {datetime.utcnow().strftime('%d %b %Y, %H:%M:%S')} | Source: YouTube video pages via yt-dlp | Video IDs and links are provided in the companion JSON/CSV.", styles["Small"])]
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica",7)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(10*mm, 7*mm, "Class 11 Maths | Lecture metadata")
        canvas.drawRightString(page[0]-10*mm, 7*mm, f"Page {document.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

def xml_escape(value):
    from xml.sax.saxutils import escape
    return escape(safe(value))

def main():
    rows=[]
    for item in LECTURES:
        print(f"Fetching {item[0]}/20: {item[1]} - {item[2]}", flush=True)
        row=fetch_one(item)
        rows.append(row)
        print(f"  {row['status']} | {row['duration']} | {row['upload_date']} | {row.get('error') or row.get('title')}", flush=True)
    json_path=OUT/"class11_maths_metadata.json"
    csv_path=OUT/"class11_maths_metadata.csv"
    pdf_path=OUT/"Class11_Maths_Lecture_Metadata_Report.pdf"
    json_path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    with csv_path.open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    build_pdf(rows,pdf_path)
    ok=sum(r["status"]=="Retrieved" for r in rows)
    print(f"REPORT_READY retrieved={ok}/20 pdf={pdf_path}",flush=True)
    print(f"PDF_BYTES={pdf_path.stat().st_size}",flush=True)
    # Keep the workflow green if some individual YouTube videos are unavailable;
    # all failures are included transparently in the report.
    return 0

if __name__=="__main__":
    sys.exit(main())
