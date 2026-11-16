"""Build sample-accurate narration and sentence subtitles from real WAV files."""
import json
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "docs/phase3"
OUT = ROOT / "deliverables/phase3"
WORK = ROOT / ".tools/phase3"
board = json.loads((QA / "storyboard.json").read_text(encoding="utf-8"))
RATE = 24000

def stamp(t):
    n = round(t * 1000)
    return f"{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}"

for v in board["videos"]:
    spoken = 0
    for s in v["scenes"]:
        s["speech"] = []
        for i, line in enumerate(s["lines"]):
            f = WORK / "speech" / f"{v['id']}_{s['id']}_{i:02}.wav"
            with wave.open(str(f), "rb") as w:
                assert w.getframerate() == RATE and w.getsampwidth() == 2 and w.getnchannels() == 1
                n = w.getnframes()
            s["speech"].append({"text": line, "file": str(f.relative_to(ROOT)).replace("\\", "/"), "samples": n})
            spoken += n
    pause_samples = round(.16 * RATE)
    base = spoken + pause_samples * sum(len(s["lines"]) - 1 for s in v["scenes"])
    spare = 170 * RATE - base
    assert spare > len(v["scenes"]) * .65 * RATE, (v["id"], spoken / RATE, spare / RATE)
    scene_spare = spare // len(v["scenes"])
    frames = []
    cursor = 0
    subs = []
    for si, s in enumerate(v["scenes"]):
        s["start"] = cursor / RATE
        lead = round(.4 * RATE)
        frames.append(b"\0\0" * lead)
        cursor += lead
        for li, speech in enumerate(s["speech"]):
            speech["start"] = cursor / RATE
            with wave.open(str(ROOT / speech["file"]), "rb") as w:
                data = w.readframes(w.getnframes())
            frames.append(data)
            cursor += speech["samples"]
            speech["end"] = cursor / RATE
            subs.append(speech)
            if li < len(s["speech"]) - 1:
                frames.append(b"\0\0" * pause_samples)
                cursor += pause_samples
        tail = scene_spare - lead
        if si == len(v["scenes"]) - 1:
            tail += spare % len(v["scenes"])
        frames.append(b"\0\0" * tail)
        cursor += tail
        s["end"] = cursor / RATE
        s["duration"] = s["end"] - s["start"]
    assert cursor == 170 * RATE
    with wave.open(str(WORK / f"{v['id']}_narration.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(frames))
    srt = "\n\n".join(f"{i}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text']}" for i, s in enumerate(subs, 1)) + "\n"
    (OUT / f"{v['name']}.srt").write_text(srt, encoding="utf-8-sig")
    v["duration"] = cursor / RATE
    v["speech_seconds"] = spoken / RATE
    (OUT / f"{v['name']}_分镜脚本.md").write_text(
        f"# {v['name']}分镜脚本\n\n1920×1080，25帧每秒。中间900像素为真实网站录像，顶部80像素为章节栏，底部100像素为字幕区。中文旁白为本地合成语音。\n\n|时段|章节|实际操作|\n|---|---|---|\n" + "\n".join(f"|{stamp(s['start'])}—{stamp(s['end'])}|{s['title']}|{s['action']}|" for s in v["scenes"]) + "\n", encoding="utf-8")
    print(v["id"], "speech", round(v["speech_seconds"], 3), "total", v["duration"], [(s["id"], round(s["duration"], 2)) for s in v["scenes"]])
(QA / "timeline.json").write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
