# -*- coding: utf-8 -*-
"""내레이션 TTS 생성.
edge-tts 는 클립 앞뒤로 1초 남짓 묵음을 붙인다 — 그대로 쓰면 타임라인이 밀리므로
잘라낸 뒤 배치한다. 배정 시간을 못 맞추면 말 속도를 한 단계씩 올리되,
홍보 톤이 무너지지 않는 +18% 까지만 쓴다."""
import asyncio, os, subprocess, sys, wave
import numpy as np, edge_tts, imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bp_narration import LINES, VOICE, PITCH, RATES

WORK = os.environ.get('PROMO_WORK', os.path.join(HERE, '_work'))
VDIR = os.path.join(WORK, 'voice'); os.makedirs(VDIR, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe(); SR = 48000

async def _tts(text, rate, path):
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=PITCH).save(path)

def _wav(mp3, wav):
    subprocess.run([FF,'-y','-loglevel','error','-i',mp3,'-ac','1','-ar',str(SR),wav], check=True)

def _read(w):
    with wave.open(w,'rb') as f:
        return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32)/32768.

def trim(a, thr=0.012, pad=0.05):
    """앞뒤 묵음 제거 (20ms 창 RMS 기준), 양쪽에 50ms 만 남긴다."""
    n = int(SR*0.02); m = len(a)//n*n
    if m == 0: return a
    r = np.sqrt((a[:m].reshape(-1,n)**2).mean(axis=1))
    idx = np.where(r > thr)[0]
    if len(idx) == 0: return a
    s = max(0, int(idx[0]*n - pad*SR)); e = min(len(a), int((idx[-1]+1)*n + pad*SR))
    return a[s:e]

def build():
    clips = []
    for i, l in enumerate(LINES):
        mp3 = os.path.join(VDIR,'l%02d.mp3'%i); wav = os.path.join(VDIR,'l%02d.wav'%i)
        best = None
        for r in RATES:
            asyncio.run(_tts(l['text'], r, mp3)); _wav(mp3, wav)
            a = trim(_read(wav)); d = len(a)/SR
            best = (r, d, a)
            if d <= l['limit']: break
        r, d, a = best
        ok = 'OK ' if d <= l['limit'] + 0.02 else '초과'
        print('  %2d  %s  %-5s  %4.2fs / %.1fs  %s' % (i, ok, r, d, l['limit'], l['text'][:30]), flush=True)
        clips.append(dict(i=i, start=l['start'], dur=d, rate=r, audio=a))
    over = [c for c in clips if c['dur'] > LINES[c['i']]['limit'] + 0.02]
    print('\n%d줄 · 시간 초과 %d줄' % (len(clips), len(over)))
    bad = 0
    for a, b in zip(clips, clips[1:]):
        gap = b['start'] - (a['start'] + a['dur'])
        if gap < 0:
            bad += 1; print('  겹침: %d->%d  %.2fs' % (a['i'], b['i'], -gap))
    print('겹침 %d건' % bad)
    return clips

if __name__ == '__main__':
    build()
