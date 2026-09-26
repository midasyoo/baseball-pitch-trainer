# -*- coding: utf-8 -*-
"""프레임 캡처 — 샷마다 setup 을 실행하고, 프레임마다 t/카메라를 찍어 렌더한 뒤 캡처한다.
캡처 속도와 무관하게 결과가 같다(결정적). 이미 있는 프레임은 건너뛰므로 중단 후 재개 가능."""
import os, sys, time, argparse
S = os.environ.get("PROMO_WORK", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_work"))
sys.path.insert(0, S)
from bpshot import Session
from bp_story import SHOTS, FPS, TOTAL

RAW = os.path.join(S, 'bp_raw')
os.makedirs(RAW, exist_ok=True)

def frame_path(i): return os.path.join(RAW, 'f%05d.png' % i)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=TOTAL)
    ap.add_argument('--port', type=int, default=9480)
    ap.add_argument('--tag', default='cap')
    a = ap.parse_args()

    # 샷 경계 계산
    bounds, t = [], 0
    for s in SHOTS:
        bounds.append((t, t + s['n'], s)); t += s['n']

    todo = [i for i in range(a.start, a.end) if not os.path.exists(frame_path(i))]
    if not todo:
        print('할 일 없음 (%d~%d 이미 완료)' % (a.start, a.end)); return
    print('캡처 대상 %d 프레임 (%d~%d)' % (len(todo), a.start, a.end), flush=True)

    s = Session(port=a.port, w=1920, h=1080, tag=a.tag)
    try:
        s.goto('pitch=slider&sub=GRIP')
        if not s.js('!!window.__CAP'): raise RuntimeError('__CAP 훅 없음')
        cur_shot = None
        done = 0; t0 = time.time()
        for i in todo:
            lo, hi, shot = next(b for b in bounds if b[0] <= i < b[1])
            if shot is not cur_shot:
                if shot.get('setup'): s.js(shot['setup'])
                time.sleep(2.2 if shot.get('setup') else 0.2)   # 모델/장면 전환 안정화
                cur_shot = shot
            n = hi - lo
            u = (i - lo) / max(n - 1, 1)
            per = shot.get('per')
            if per: s.js(per.replace('{u}', '%.6f' % u))
            else:   s.js('__CAP.draw();')
            s.shot(frame_path(i))
            done += 1
            if done % 25 == 0 or done == len(todo):
                el = time.time() - t0
                print('  %d/%d  %.1f fps  남은 %.1f분'
                      % (done, len(todo), done/el, (len(todo)-done)/(done/el)/60), flush=True)
    finally:
        s.close()

if __name__ == '__main__':
    main()
