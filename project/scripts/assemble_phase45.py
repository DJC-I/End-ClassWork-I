"""Trim actual browser recordings, add chapter bars and exact sentence captions."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "docs/phase4_5"
WORK = ROOT / ".tools/phase4_5"
OUT = ROOT / "deliverables/phase4_5"
sys.path.insert(0, str(ROOT / ".tools/phase3/pydeps"))
import av
from PIL import Image, ImageDraw, ImageFont

FFMPEG = ROOT / ".tools/phase3/ffmpeg.exe"
FONT = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"

def run(args, log):
    with log.open("w", encoding="utf-8") as f:
        result = subprocess.run([str(FFMPEG), "-hide_banner", "-nostdin", *map(str, args)], stdout=f, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"FFmpeg failed; see {log}")

def ass_time(t):
    n = round(t * 100)
    return f"{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}"

def wrap(s):
    if len(s) <= 43:
        return s
    mid = len(s)//2
    split = next((i+1 for i in range(mid-6, mid+7) if s[i] in "，。；、"), mid)
    return s[:split] + r"\N" + s[split:]

def assemble(vid):
    board = json.loads((QA / "timeline.json").read_text(encoding="utf-8"))
    video = next(v for v in board["videos"] if v["id"] == vid)
    evidence = json.loads((QA / f"{vid}-recording.json").read_text(encoding="utf-8"))
    assert len(evidence["scenes"]) == len(video["scenes"]) and not evidence["errors"]
    folder = WORK / vid
    folder.mkdir(exist_ok=True)
    trims = []
    logs = QA / "logs"
    logs.mkdir(exist_ok=True)
    for idx, (scene, captured) in enumerate(zip(video["scenes"], evidence["scenes"]), 1):
        assert scene["id"] == captured["id"]
        raw = ROOT / captured["raw"]
        with av.open(str(raw)) as container:
            raw_duration = container.duration / av.time_base
            assert container.streams.video[0].width == 1920 and container.streams.video[0].height == 900
        offset = max(0, raw_duration - captured["tail_seconds"])
        scene_frames = round(scene["end"]*25)-round(scene["start"]*25)
        clip = folder / f"{idx:02}_{scene['id']}.mp4"
        header = folder / f"{idx:02}_header.png"
        im = Image.new("RGB", (1920,80), "#10171f")
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((24,15,112,64),radius=8,fill="#b6f36a")
        d.text((42,23),f"赛题{'一' if vid=='growth' else '二'}",font=ImageFont.truetype(BOLD,24),fill="#10171f")
        d.text((137,20),scene["title"],font=ImageFont.truetype(BOLD,28),fill="#f1f5f9")
        tag=f"SkyRoute AI  |  真实网站演示  |  教学模拟  |  {idx:02}/{len(video['scenes']):02}"
        font=ImageFont.truetype(FONT,20)
        d.text((1885-d.textlength(tag,font=font),25),tag,font=font,fill="#afbdca")
        d.line((0,78,1920,78),fill="#32404c",width=2)
        im.save(header)
        ass = folder / f"{idx:02}.ass"
        caption = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,34,&H00FFFFFF,&H00FFFFFF,&H0010171F,&H0010171F,0,0,0,0,100,100,0,0,1,1,0,2,80,80,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        for line in scene["speech"]:
            caption += f"Dialogue: 0,{ass_time(line['start']-scene['start'])},{ass_time(line['end']-scene['start'])},Default,,0,0,0,,{wrap(line['text'])}\n"
        ass.write_text(caption,encoding="utf-8-sig")
        # Relative ASS path and slash paths avoid drive-colon filter escaping.
        filt=f"[0:v]fps=25,setsar=1,pad=1920:1080:0:80:color=0x10171f[base];[base][1:v]overlay=0:0,ass={ass.relative_to(ROOT).as_posix()}[out]"
        run(["-ss",f"{offset:.6f}","-i",raw,"-i",header,"-filter_complex",filt,"-map","[out]","-an","-frames:v",scene_frames,"-c:v","h264_nvenc","-preset","p4","-cq","20","-b:v","0","-pix_fmt","yuv420p","-y",clip], logs / f"{vid}-{scene['id']}-encode.log")
        trims.append({"scene":scene["id"],"raw":captured["raw"],"raw_duration":raw_duration,"trim_start":offset,"output_frames":scene_frames,"output":str(clip.relative_to(ROOT)).replace("\\","/")})
        print(vid,scene["id"],"encoded",scene_frames,"frames",flush=True)
    concat = folder / "concat.txt"
    concat.write_text("\n".join(f"file '{(ROOT/t['output']).as_posix()}'" for t in trims),encoding="utf-8")
    output=OUT/f"{video['name']}.mp4"
    run(["-f","concat","-safe","0","-i",concat,"-i",WORK/f"{vid}_narration.wav","-map","0:v:0","-map","1:a:0","-c:v","copy","-af","loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000:async=1:first_pts=0","-c:a","aac","-b:a","192k","-ac","2","-t",str(video["duration"]),"-movflags","+faststart","-metadata","title="+video["name"],"-metadata","comment=Actual local website recording; synthetic teaching data; Chinese synthetic narration","-y",output],logs/f"{vid}-mux.log")
    report={"file":str(output.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"bytes":output.stat().st_size,"trims":trims,"spoken_seconds":video["speech_seconds"],"target_seconds":video["duration"],"voice":"zh-CN-XiaoxiaoNeural","voice_rate":video["voice_rate"],"video_encoder":"h264_nvenc","subtitle_burned":True,"website_content_modified":True,"modification_scope":"About page removed two requested components; core functions unchanged"}
    (QA/f"{vid}-assembly.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DONE",report["file"],report["bytes"],flush=True)

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("video",choices=["growth","logistics"]);assemble(p.parse_args().video)
