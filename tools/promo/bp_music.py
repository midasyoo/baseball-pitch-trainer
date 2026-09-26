# -*- coding: utf-8 -*-
"""배경음 합성 — 외부 음원을 쓰지 않는다(저작권 문제 없음).
영상 구성에 맞춰 구간별 강약을 준다: 도입은 차분하게, 6구종 몽타주에서 리듬을 얹고,
실제 연습은 다시 가라앉히고, 마지막에 한 번 부풀린다."""
import numpy as np

SR = 48000
BPM = 112
BEAT = 60.0 / BPM          # 0.536s
BAR = BEAT * 4

def note(n):               # MIDI 번호 -> Hz
    return 440.0 * 2 ** ((n - 69) / 12.0)

# Am - F - C - G (4마디 반복) · 밝지만 과하지 않은 진행
PROG = [
    (57, [57, 60, 64, 69]),   # Am
    (53, [53, 57, 60, 65]),   # F
    (48, [48, 55, 60, 64]),   # C
    (55, [50, 55, 59, 62]),   # G
]

def env(n, a, d, s, r, sus=0.75):
    """ADSR — 샘플 수 n"""
    a, d, r = int(a*SR), int(d*SR), int(r*SR)
    s = max(0, n - a - d - r)
    return np.concatenate([
        np.linspace(0, 1, a, endpoint=False) if a else np.zeros(0),
        np.linspace(1, sus, d, endpoint=False) if d else np.zeros(0),
        np.full(s, sus),
        np.linspace(sus, 0, r) if r else np.zeros(0),
    ])[:n]

def pad(freqs, dur, amp):
    """패드 — 배음을 더하고 살짝 디튠해 두툼하게"""
    n = int(dur*SR); t = np.arange(n)/SR
    out = np.zeros(n)
    for f in freqs:
        vib = 1 + 0.0016*np.sin(2*np.pi*4.3*t + f)
        for h, ha in ((1, 1.0), (2, 0.34), (3, 0.13), (4, 0.06)):
            for det in (-1, 1):
                ff = f*h*(1 + det*0.0012)*vib
                out += ha*np.sin(2*np.pi*ff*t + det*f*0.7)
    out /= (len(freqs)*4.2)
    return out * env(n, 0.55, 0.5, 0, 0.9, 0.82) * amp

def pluck(f, dur, amp):
    n = int(dur*SR); t = np.arange(n)/SR
    e = np.exp(-t*7.5)
    s = np.sin(2*np.pi*f*t) + 0.36*np.sin(2*np.pi*2*f*t) + 0.12*np.sin(2*np.pi*3*f*t)
    return s*e*amp*0.5

def bass(f, dur, amp):
    n = int(dur*SR); t = np.arange(n)/SR
    s = np.sin(2*np.pi*f*t) + 0.2*np.sin(2*np.pi*2*f*t)
    return np.tanh(s*1.25) * env(n, 0.012, 0.16, 0, 0.2, 0.62) * amp

def kick(amp):
    n = int(0.30*SR); t = np.arange(n)/SR
    f = 120*np.exp(-t*26) + 44
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*9.5) * amp

def hat(amp, dur=0.055):
    n = int(dur*SR)
    rng = np.random.default_rng(7)
    x = rng.normal(0, 1, n)
    x = np.diff(np.concatenate([[0], x]))          # 간이 하이패스
    return x*np.exp(-np.arange(n)/SR*70)*amp*0.22

def add(buf, sig, at):
    i = int(at*SR); j = min(len(buf), i+len(sig))
    if i >= len(buf): return
    buf[i:j] += sig[:j-i]

def reverb(x, sr=SR):
    out = x.copy()
    for d, g in ((0.031, .28), (0.053, .22), (0.079, .16), (0.113, .11), (0.157, .07)):
        k = int(d*sr)
        out[k:] += x[:-k]*g
    return out

def gain_at(t):
    """구간별 음량 — 타임라인(초) 기준"""
    if t < 4.0:    return 0.62 + 0.28*(t/4.0)        # 타이틀에서 서서히
    if t < 32.0:   return 0.80                        # 원리 이해
    if t < 44.0:   return 1.00                        # 6구종 몽타주 — 가장 세게
    if t < 57.0:   return 0.76                        # 실제 연습
    if t < 58.6:   return 0.76 + 0.30*((t-57.0)/1.6)  # 클로징 부풀림
    return max(0.0, 1.06*(1 - (t-58.6)/1.4))          # 페이드아웃

def build(total=60.0):
    n = int(total*SR)
    pads = np.zeros(n); arps = np.zeros(n); bs = np.zeros(n); dr = np.zeros(n)
    bar_i = 0; t = 0.0
    while t < total:
        root, chord = PROG[bar_i % len(PROG)]
        add(pads, pad([note(m) for m in chord], BAR*1.06, 0.30), t)
        add(bs, bass(note(root-12), BEAT*3.6, 0.42), t)
        # 8분음 아르페지오
        seq = [chord[0], chord[2], chord[1], chord[3], chord[2], chord[3], chord[1], chord[2]]
        for k, m in enumerate(seq):
            at = t + k*BEAT/2
            if at >= total: break
            add(arps, pluck(note(m+12), 0.5, 0.17 if k % 2 == 0 else 0.11), at)
        # 리듬은 몽타주 구간과 클로징에만
        if 31.5 <= t < 44.5 or t >= 56.8:
            for k in (0, 2):
                add(dr, kick(0.42), t + k*BEAT)
            for k in range(8):
                add(dr, hat(0.30), t + k*BEAT/2)
        t += BAR; bar_i += 1

    mix = reverb(pads*0.95 + arps*0.85)*0.55 + pads*0.55 + arps*0.5 + bs*0.9 + dr*0.8
    g = np.array([gain_at(i/SR) for i in range(0, n, 256)])
    g = np.repeat(g, 256)[:n]
    mix *= g
    mx = np.abs(mix).max()
    if mx > 0: mix /= mx
    return mix[:n].astype(np.float32)

if __name__ == '__main__':
    import wave, os
    m = build()
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'music.wav')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with wave.open(p,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m*0.9*32767).astype(np.int16).tobytes())
    print('배경음 %.2fs -> %s' % (len(m)/SR, p))
