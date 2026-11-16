"""Decode final movies, inspect streams and compare narration timing to source PCM."""
import array
import hashlib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/"docs/phase4_6"
WORK=ROOT/".tools/phase4_6"
OUT=ROOT/"deliverables/phase4_6"
sys.path.insert(0,str(ROOT/".tools/phase3/pydeps"))
import av
import numpy as np
from PIL import Image,ImageDraw,ImageFont

FONT=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",20)
board=json.loads((QA/"timeline.json").read_text(encoding="utf-8"))
results=[]
for video in board["videos"]:
    vid=video["id"]
    final=OUT/f"{video['name']}.mp4"
    assert final.is_file() and final.stat().st_size>1000000
    assembly=json.loads((QA/f"{vid}-assembly.json").read_text(encoding="utf-8"))
    recording=json.loads((QA/f"{vid}-recording.json").read_text(encoding="utf-8"))
    assert not recording["errors"] and not recording["external_requests"]
    assert len(recording["scenes"])==len(video["scenes"])
    sha=hashlib.sha256(final.read_bytes()).hexdigest()
    assert sha==assembly["sha256"]
    srt=(OUT/f"{video['name']}.srt").read_text(encoding="utf-8-sig")
    actual=[block.splitlines()[2:] for block in srt.strip().split("\n\n")]
    expected=[s["text"] for scene in video["scenes"] for s in scene["speech"]]
    assert ["\n".join(s) for s in actual]==expected
    previous=0
    for scene in video["scenes"]:
        for line in scene["speech"]:
            assert previous <= line["start"] < line["end"] <= video["duration"]
            previous=line["end"]
    (QA/"samples"/vid).mkdir(parents=True,exist_ok=True)
    sample_times=[]
    for scene in video["scenes"]:
        sample_times.append((scene["id"],(scene["start"]+scene["end"])/2))
    with av.open(str(final)) as c:
        v=c.streams.video[0]
        a=c.streams.audio[0]
        info={"duration":c.duration/av.time_base,"width":v.width,"height":v.height,"video_codec":v.codec_context.name,"pixel_format":v.codec_context.format.name,"fps":float(v.average_rate),"audio_codec":a.codec_context.name,"audio_sample_rate":a.rate,"audio_channels":a.codec_context.channels}
        assert info["width"]==1920 and info["height"]==1080 and info["fps"]==25
        assert info["video_codec"]=="h264" and info["pixel_format"]=="yuv420p"
        assert info["audio_codec"]=="aac" and info["audio_sample_rate"]==48000 and info["audio_channels"]==2
        assert 160 <= info["duration"] <= 180
        frames=0
        previous=-1
        todo=iter(sample_times)
        next_sample=next(todo,None)
        thumbnails=[]
        for frame in c.decode(video=0):
            assert frame.time > previous
            previous=frame.time
            frames+=1
            if next_sample and frame.time>=next_sample[1]:
                name,t=next_sample
                im=frame.to_image()
                im.save(QA/"samples"/vid/f"{name}.png")
                im.crop((0,980,1920,1080)).save(QA/"samples"/vid/f"{name}-subtitle.png")
                thumb=im.resize((640,360))
                tile=Image.new("RGB",(640,396),"#10171f")
                tile.paste(thumb,(0,36))
                ImageDraw.Draw(tile).text((10,6),f"{t:.2f}s  {name}",font=FONT,fill="white")
                thumbnails.append(tile)
                next_sample=next(todo,None)
        assert frames==round(video["duration"]*25) and next_sample is None
        info["decoded_video_frames"]=frames
    contact=Image.new("RGB",(1280,396*((len(thumbnails)+1)//2)),"#0e131a")
    for i,thumb in enumerate(thumbnails): contact.paste(thumb,((i%2)*640,(i//2)*396))
    contact.save(QA/f"{vid}-contact.jpg",quality=92)
    pcm=[]
    with av.open(str(final)) as c:
        resampler=av.AudioResampler(format="s16",layout="mono",rate=24000)
        audio_frames=0
        for frame in c.decode(audio=0):
            audio_frames+=1
            for f in resampler.resample(frame): pcm.append(f.to_ndarray().reshape(-1).copy())
        for f in resampler.resample(None): pcm.append(f.to_ndarray().reshape(-1).copy())
    decoded=np.concatenate(pcm).astype(np.float64)
    with wave.open(str(WORK/f"{vid}_narration.wav"),"rb") as w:
        master=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float64)
    checks=[]
    for scene in video["scenes"]:
        # Middle of first sentence gives active speech instead of lead silence.
        line=scene["speech"][0]
        at=round(((line["start"]+line["end"])/2)*24000)
        src=master[at:at+12000]
        best=(-1,None)
        for offset in range(-2400,2401,24):
            segment=decoded[at+offset:at+offset+len(src)]
            if len(segment)!=len(src):continue
            score=float(np.dot(src,segment)/(np.linalg.norm(src)*np.linalg.norm(segment)+1e-9))
            if score>best[0]: best=(score,offset)
        assert best[0]>.9,(vid,scene["id"],best)
        assert abs(best[1]/24)<80,(vid,scene["id"],best)
        checks.append({"scene":scene["id"],"sample_time":at/24000,"correlation":round(best[0],6),"best_audio_offset_ms":best[1]/24})
    rms=float(np.sqrt(np.mean(decoded**2)))
    peak=float(np.max(np.abs(decoded)))
    assert rms>500 and peak<32768
    log=QA/"logs"/f"{vid}-full-decode.log"
    with log.open("w",encoding="utf-8") as f:
        proc=subprocess.run([str(ROOT/".tools/phase3/ffmpeg.exe"),"-hide_banner","-v","error","-xerror","-err_detect","explode","-i",str(final),"-map","0:v:0","-map","0:a:0","-f","null","-"],stdout=f,stderr=subprocess.STDOUT)
    assert proc.returncode==0
    result={"file":str(final.relative_to(ROOT)).replace("\\","/"),"sha256":sha,"bytes":final.stat().st_size,**info,"decoded_audio_frames":audio_frames,"full_ffmpeg_decode_passed":True,"srt_sentences":len(expected),"srt_matches_narration":True,"audio_rms_pcm16":round(rms,2),"audio_peak_pcm16":peak,"audio_alignment_checks":checks,"actual_recorded_scenes":len(recording["scenes"]),"browser_errors":recording["errors"],"external_requests":recording["external_requests"],"visual_review_contact":f"docs/phase4_6/{vid}-contact.jpg"}
    results.append(result)
    print(vid,"passed",info["duration"],"seconds",frames,"frames",len(expected),"captions",flush=True)
assert not list(OUT.rglob("*.zip"))
(QA/"verification.json").write_text(json.dumps({"phase":"4.6","technical_passed":True,"outputs":results,"human_audio_listening_claimed":False,"later_phases_started":False},ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"SHA256SUMS.txt").write_text("\n".join(f"{r['sha256']}  {Path(r['file']).name}" for r in results)+"\n",encoding="utf-8")
