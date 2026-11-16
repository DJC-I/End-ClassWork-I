// Validate actual HTML5 playback of both final MP4 files through HTTP byte ranges.
const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const http=require('node:http');
const fs=require('node:fs');
const fsp=require('node:fs/promises');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
(async()=>{
  const timeline=JSON.parse(await fsp.readFile(path.join(ROOT,'docs/phase4_5/timeline.json'),'utf8'));
  const files=timeline.videos.map(v=>path.join(ROOT,'deliverables/phase4_5',v.name+'.mp4'));
  const server=http.createServer((req,res)=>{
    if(req.url==='/') {res.setHeader('Content-Type','text/html;charset=utf-8');res.end('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>第4.5阶段视频播放检验</title><body style="margin:0;background:#10171f"><video controls style="width:100vw;height:100vh" preload="auto"></video></body></html>');return;}
    const match=/^\/movie(\d)$/.exec(req.url);
    if(!match||!files[Number(match[1])]){res.writeHead(404);res.end();return;}
    const file=files[Number(match[1])],size=fs.statSync(file).size;
    res.setHeader('Content-Type','video/mp4');res.setHeader('Accept-Ranges','bytes');
    const range=req.headers.range;
    if(range){const m=/bytes=(\d+)-(\d*)/.exec(range);const start=Number(m[1]),end=m[2]?Math.min(Number(m[2]),size-1):size-1;res.writeHead(206,{'Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':end-start+1});fs.createReadStream(file,{start,end}).pipe(res);}
    else {res.writeHead(200,{'Content-Length':size});fs.createReadStream(file).pipe(res);}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({channel:'msedge',headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  const results=[];
  try {
    for(let i=0;i<files.length;i++){
      const page=await browser.newPage({viewport:{width:1920,height:1080}});
      const errors=[];page.on('pageerror',e=>errors.push(e.message));
      await page.goto(`http://127.0.0.1:${server.address().port}/`);
      const result=await page.evaluate(async index=>{
        const video=document.querySelector('video');video.src='/movie'+index;video.volume=.15;video.muted=false;
        await new Promise((resolve,reject)=>{video.onloadedmetadata=resolve;video.onerror=()=>reject(new Error('Video metadata failed'));});
        const result={duration:video.duration,width:video.videoWidth,height:video.videoHeight,muted:video.muted,samples:[]};
        for(const t of [2,video.duration/2,video.duration-5]){
          video.currentTime=t;
          await new Promise(resolve=>video.addEventListener('seeked',resolve,{once:true}));
          const before=video.getVideoPlaybackQuality().totalVideoFrames;
          await video.play();await new Promise(resolve=>setTimeout(resolve,1700));video.pause();
          result.samples.push({requested:t,played_to:video.currentTime,decoded_frames:video.getVideoPlaybackQuality().totalVideoFrames-before,ready_state:video.readyState,error:video.error&&video.error.message});
        }
        video.currentTime=video.duration-1;
        await new Promise(resolve=>video.addEventListener('seeked',resolve,{once:true}));
        await video.play();await new Promise((resolve,reject)=>{video.addEventListener('ended',resolve,{once:true});setTimeout(()=>{if(!video.ended)reject(new Error('No ended event'));},5000)});
        result.ended=video.ended;result.end_time=video.currentTime;return result;
      },i);
      expect(result.duration).toBe(timeline.videos[i].duration);expect(result.width).toBe(1920);expect(result.height).toBe(1080);expect(result.ended).toBeTruthy();
      for(const sample of result.samples){expect(sample.played_to).toBeGreaterThan(sample.requested+1);expect(sample.decoded_frames).toBeGreaterThan(15);expect(sample.error).toBeFalsy();}
      expect(errors).toEqual([]);
      results.push({file:path.relative(ROOT,files[i]).replaceAll('\\','/'),browser:'Microsoft Edge',...result,errors});
      await page.screenshot({path:path.join(ROOT,'docs/phase4_5',timeline.videos[i].id+'-playback-ended.png')});
      await page.close();console.log(timeline.videos[i].id,'actual playback passed');
    }
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
  await fsp.writeFile(path.join(ROOT,'docs/phase4_5/playback.json'),JSON.stringify({passed:true,outputs:results},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
