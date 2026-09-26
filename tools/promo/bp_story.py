# -*- coding: utf-8 -*-
import os
"""baseball-pitch-trainer 1분 홍보 영상 — 스토리보드 정의.
24 fps · 1440 frames · 1920x1080
큰 줄기 둘: ① 원리 이해  ② 실제 연습
"""
FPS = 24

# kind: 'play'(3D 화면) / 'card'(전면 카드)
# js   : 프레임 진입 전 1회 실행 (샷 시작 시)
# per  : 프레임마다 실행할 JS 템플릿 — {u} 는 샷 내 진행도 0..1
SHOTS = [
  # ── 타이틀 ───────────────────────────────────────────────
  dict(n=96, kind='title', setup="__CAP.selectPitch('slider'); __CAP.setSubMode('GRIP'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.orbitSet({u}*26-13); __CAP.draw();",
       title='BASEBALL PITCH TRAINER',
       sub='야구 투구 트레이닝 3D 시뮬레이터',
       note='원리를 눈으로 보고 · 손으로 따라 한다'),

  # ── ① 원리 이해 ──────────────────────────────────────────
  dict(n=72, kind='card', chapter='①', title='원리 이해',
       sub='왜 그렇게 휘는지부터 이해한다',
       note='그립 → 릴리스 → 회전 → 투구 자세 → 궤적'),

  dict(n=96, kind='play', setup="__CAP.selectPitch('slider'); __CAP.setSubMode('GRIP'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.orbitSet({u}*50-25); __CAP.draw();",
       cap=('① 그립', '어느 손가락이 실밥 어디에 닿는가',
            '접촉점만 바꾸면 손 모양은 저절로 만들어진다')),

  dict(n=120, kind='play', setup="__CAP.setSubMode('RELEASE'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.seek({u}); __CAP.orbitSet({u}*16-8); __CAP.draw();",
       cap=('② 릴리스', '엄지가 먼저, 손끝이 나중에 떨어진다',
            '이 0.02초의 순서가 회전을 결정한다')),

  dict(n=96, kind='play', setup="__CAP.setSubMode('SPIN'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.spin(0.115); __CAP.orbitSet({u}*20-10); __CAP.draw();",
       cap=('③ 회전', '회전축이 기울면 공은 옆으로 미끄러진다',
            '축 · 방향 · 회전수(RPM)를 눈으로 본다')),

  dict(n=96, kind='play', setup="__CAP.setSubMode('MOTION'); __CAP.setCameraView('PITCHER',true); __CAP.orbitReset();",
       per="__CAP.seek({u}); __CAP.orbitSet({u}*18-9); __CAP.draw();",
       cap=('④ 투구 자세', 'P0 세트부터 P5 팔로스루까지',
            '몸 전체가 만들어 내는 힘의 순서')),

  dict(n=96, kind='play', setup="__CAP.setSubMode('PATH'); __CAP.setCameraView('CATCHER',true); __CAP.orbitReset();",
       per="__CAP.seek({u}*0.995); __CAP.draw();",
       cap=('⑤ 궤적', '스트라이크 존으로 어떻게 파고드는가',
            '포수 뒤에서 본 공의 실제 경로')),

  dict(n=96, kind='play', setup="__CAP.setSubMode('PATH'); __CAP.setCameraView('BATTER',true); __CAP.orbitReset();",
       per="__CAP.seek(0.30+{u}*0.69); __CAP.draw();",
       cap=('타자의 시점', '실제로 타석에서 이렇게 보인다',
            '왜 못 치는지 직접 확인해 본다')),
]

# ── 6구종 쇼케이스 (48프레임 × 6 = 288) ──────────────────
PITCHES6 = [
  ('twoSeam',     '투심 패스트볼', '실밥을 따라 쥐고 살짝 가라앉힌다'),
  ('sinker',      '싱커',         '더 깊이 떨어뜨리는 땅볼 유도구'),
  ('slider',      '슬라이더',      '옆으로 미끄러지듯 휘어 나간다'),
  ('curveball',   '커브볼',        '위에서 아래로 크게 떨어진다'),
  ('forkball',    '포크볼',        '검지·중지를 벌려 회전을 죽인다'),
  ('knuckleball', '너클볼',        '회전이 거의 없어 제멋대로 흔들린다'),
]
for pid, pname, pdesc in PITCHES6:
    SHOTS.append(dict(n=24, kind='play',
        setup="__CAP.selectPitch('%s'); __CAP.setSubMode('GRIP'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();" % pid,
        per="__CAP.orbitSet({u}*44-22); __CAP.draw();",
        cap=(pname, pdesc, '그립')))
    SHOTS.append(dict(n=24, kind='play',
        setup="__CAP.setSubMode('PATH'); __CAP.setCameraView('BATTER',true);",
        per="__CAP.seek(0.32+{u}*0.66); __CAP.draw();",
        cap=(pname, pdesc, '타자 시점 궤적')))

# ── ② 실제 연습 ──────────────────────────────────────────
SHOTS += [
  dict(n=48, kind='card', chapter='②', title='실제 연습',
       sub='3D 그립을 보며 진짜 공으로 따라 한다',
       note='연습 순서 · 카메라 그립 체크 · 자가진단'),

  dict(n=88, kind='play', setup="__CAP.setTopMode('PRACTICE'); __CAP.selectPitch('slider'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.orbitSet({u}*40-20); __CAP.draw();",
       cap=('실제 연습', '접촉점을 그대로 손에 옮긴다',
            '연습 순서와 안전 수칙을 함께 안내')),

  dict(n=88, kind='play', setup="__CAP.selectPitch('forkball'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.orbitSet({u}*40-20); __CAP.draw();",
       cap=('카메라 그립 체크', '공을 쥔 손을 찍으면 AI가 손가락을 읽는다',
            '사진은 기기 밖으로 나가지 않는다')),

  dict(n=88, kind='play', setup="__CAP.selectPitch('knuckleball'); __CAP.setCameraView('GRIP',true); __CAP.orbitReset();",
       per="__CAP.orbitSet({u}*40-20); __CAP.draw();",
       cap=('자가진단', '3D 그립과 내 손을 비교하며 답한다',
            '청소년 안전 수칙 — 변화구 반복 투구는 지도자와 함께')),

  dict(n=72, kind='outro', title='BASEBALL PITCH TRAINER',
       sub='14개 구종 · 설치 없이 브라우저에서 바로',
       note='midasyoo.github.io/baseball-pitch-trainer'),
]

TOTAL = sum(s['n'] for s in SHOTS)
if __name__ == '__main__':
    print('샷', len(SHOTS), '· 총 프레임', TOTAL, '· 길이 %.2fs' % (TOTAL/FPS))
    t = 0
    for i, s in enumerate(SHOTS):
        lab = s.get('title') or (s.get('cap') or ('',))[0]
        print('  %2d  %5.1fs  %3df  %-7s %s' % (i, t/FPS, s['n'], s['kind'], lab))
        t += s['n']
