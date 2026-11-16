"""Decode actual latest media and make chapter-sampled review sheets locally."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / ".tools/phase5/pydeps"), str(ROOT / ".tools/phase3/pydeps")]
from PIL import Image, ImageDraw
import av

OUT = ROOT / "docs/phase5"
OUT.mkdir(parents=True, exist_ok=True)
results = []
for slug, name in [("growth", "赛题一_DataClawHub平台运营方案"), ("logistics", "赛题二_气象物流AI风险决策系统")]:
    p = ROOT / "deliverables/phase4_6" / (name + ".mp4")
    assembly = json.loads((ROOT / f"docs/phase4_6/{slug}-assembly.json").read_text(encoding="utf-8"))
    targets = []
    start = 0
    for scene in assembly["trims"]:
        count = scene["output_frames"]
        targets.append((start + count // 2, scene["scene"]))
        start += count
    frames = {}
    with av.open(str(p)) as video:
        stream = video.streams.video[0]
        metadata = dict(video.metadata)
        duration = video.duration / av.time_base
        total = 0
        for frame in video.decode(video=0):
            for index, title in targets:
                if total == index:
                    frames[title] = frame.to_image()
            total += 1
        width, height = stream.width, stream.height
    audio_frames = 0
    with av.open(str(p)) as video:
        for frame in video.decode(audio=0):
            audio_frames += 1
    sheet = Image.new("RGB", (1440, ((len(targets)+2)//3)*300), "#eef1f0")
    draw = ImageDraw.Draw(sheet)
    for i, (index, title) in enumerate(targets):
        thumb = frames[title].resize((480, 270))
        x, y = (i % 3) * 480, (i // 3) * 300
        sheet.paste(thumb, (x, y))
        draw.text((x+8, y+275), f"{title} | {index/25:.2f}s", fill="#172c3c")
    sheet.save(OUT / f"{slug}-privacy-contact.jpg", quality=94)
    results.append({"file": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                    "duration": duration, "width": width, "height": height, "decoded_video_frames": total,
                    "decoded_audio_frames": audio_frames, "metadata": metadata, "sampled_chapters": len(targets),
                    "under_180_seconds": duration <= 180,
                    "limitations": "Chapter samples are not frame-by-frame OCR or full human listening."})
(OUT / "media-audit.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print("Decoded two actual MP4s; 21 chapter samples prepared")
