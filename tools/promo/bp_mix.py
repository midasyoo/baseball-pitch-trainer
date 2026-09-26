# -*- coding: utf-8 -*-
"""내레이션 + 배경음 믹스 → 영상에 입히기.

- 내레이션이 나오는 동안 배경음을 낮춘다(더킹).
- 컴프레서로 피크를 정리한 뒤 2패스 loudnorm 으로 -14 LUFS 에 맞춘다.
  1패스로는 피크 여유가 없어 목표에 못 닿는다(크레스트 팩터가 크다).
"""
import json, os, re, subprocess, sys, wave
import numpy as np, imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bp_music
from bp_voice import build as build_voice

SR = bp_music.SR
WORK = os.environ.get('PROMO_WORK', os.path.join(HERE, '_work')); os.makedirs(WORK, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
TOTAL = 60.0
PROJ = os.path.dirname(os.path.dirname(HERE))
VIDEO_IN  = os.path.join(PROJ, 'baseball-pitch-trainer-1min.mp4')
VIDEO_OUT = os.path.join(PROJ, 'baseball-pitch-trainer-1min-narrated.mp4')

COMP = ('acompressor=threshold=-20dB:ratio=2.6:attack=6:release=140:makeup=2,'
        'alimiter=level_in=1:limit=0.85:attack=5:release=60')

def run(args):
    return subprocess.run([FF] + args, capture_output=True, text=True, errors='replace')

def smooth(x, ms):
    k = max(1, int(SR*ms/1000.0))
    return np.convolve(x, np.ones(k)/k, mode='same')

def write_wav(path, x):
    with wave.open(path,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())

def main():
    n = int(TOTAL*SR)
    print('1) 내레이션'); clips = build_voice()
    voice = np.zeros(n)
    for c in clips:
        i = int(c['start']*SR); a = c['audio']
        j = min(n, i+len(a)); voice[i:j] += a[:j-i]

    # 더킹 게이트 — 말이 있는 구간을 넉넉히 잡고 부드럽게 잇는다
    gate = (np.abs(voice) > 0.01).astype(np.float32)
    gate = (smooth(gate, 260) > 0.02).astype(np.float32)
    gate = np.clip(smooth(gate, 420), 0, 1)

    print('2) 배경음'); music = bp_music.build(TOTAL)[:n]
    voice = voice/(np.abs(voice).max() or 1.0)*0.86
    mix = voice + music*(1.0 - 0.62*gate)*0.30
    pk = np.abs(mix).max()
    if pk > 0.99: mix *= 0.99/pk
    raw = os.path.join(WORK,'mix.wav'); write_wav(raw, mix)
    print('   내레이션 %.1fs / %.0fs · 피크 %.3f' % (gate.sum()/SR, TOTAL, np.abs(mix).max()))

    print('3) 컴프레션')
    comp = os.path.join(WORK,'mix_comp.wav')
    run(['-y','-loglevel','error','-i',raw,'-af',COMP,'-ar',str(SR),'-ac','1',comp])

    print('4) 2패스 라우드니스 정규화 (-14 LUFS / TP -1.5dB)')
    r = run(['-i',comp,'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
    m = json.loads(re.search(r'\{[^{}]*\}', r.stderr, re.S).group(0))
    print('   측정 I=%s TP=%s LRA=%s' % (m['input_i'], m['input_tp'], m['input_lra']))
    norm = os.path.join(WORK,'mix_norm.wav')
    run(['-y','-loglevel','error','-i',comp,'-af',
         'loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:'
         'measured_thresh=%s,aresample=%d' % (m['input_i'], m['input_tp'], m['input_lra'],
                                              m['input_thresh'], SR),
         '-ar',str(SR),'-ac','1','-t',str(TOTAL),norm])

    print('5) 영상에 입히기')
    run(['-y','-loglevel','error','-i',VIDEO_IN,'-i',norm,'-c:v','copy','-c:a','aac',
         '-b:a','192k','-ar',str(SR),'-ac','2','-shortest','-movflags','+faststart', VIDEO_OUT])
    print('완성 -> %s  (%.1f MB)' % (VIDEO_OUT, os.path.getsize(VIDEO_OUT)/1048576))

if __name__ == '__main__':
    main()
